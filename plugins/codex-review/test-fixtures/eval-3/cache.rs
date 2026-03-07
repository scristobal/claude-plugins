use std::collections::HashMap;
use std::sync::{Arc, Mutex};
use std::thread;
use std::time::{Duration, Instant};

pub struct Cache {
    data: Arc<Mutex<HashMap<String, CacheEntry>>>,
    max_size: usize,
}

struct CacheEntry {
    value: String,
    expires_at: Instant,
    access_count: u32,
}

impl Cache {
    pub fn new(max_size: usize) -> Self {
        Cache {
            data: Arc::new(Mutex::new(HashMap::new())),
            max_size,
        }
    }

    pub fn get(&self, key: &str) -> Option<String> {
        let map = self.data.lock().unwrap();
        match map.get(key) {
            Some(entry) => {
                if entry.expires_at < Instant::now() {
                    // Entry expired, but we don't remove it here because we hold an immutable ref
                    None
                } else {
                    Some(entry.value.clone())
                }
            }
            None => None,
        }
    }

    pub fn set(&self, key: String, value: String, ttl_secs: u64) {
        let mut map = self.data.lock().unwrap();

        if map.len() >= self.max_size {
            self.evict_oldest(&mut map);
        }

        map.insert(key, CacheEntry {
            value,
            expires_at: Instant::now() + Duration::from_secs(ttl_secs),
            access_count: 0,
        });
    }

    fn evict_oldest(&self, map: &mut HashMap<String, CacheEntry>) {
        let mut oldest_key: Option<String> = None;
        let mut lowest_count = u32::MAX;

        for (key, entry) in map.iter() {
            if entry.access_count < lowest_count {
                lowest_count = entry.access_count;
                oldest_key = Some(key.clone());
            }
        }

        if let Some(key) = oldest_key {
            map.remove(&key);
        }
    }

    pub fn cleanup_expired(&self) {
        let mut map = self.data.lock().unwrap();
        let now = Instant::now();

        let keys_to_remove: Vec<String> = map
            .iter()
            .filter(|(_, entry)| entry.expires_at < now)
            .map(|(key, _)| key.clone())
            .collect();

        for key in keys_to_remove {
            map.remove(&key);
        }
    }

    pub fn start_cleanup_thread(&self, interval_secs: u64) {
        let data = self.data.clone();
        thread::spawn(move || {
            loop {
                thread::sleep(Duration::from_secs(interval_secs));
                let mut map = data.lock().unwrap();
                let now = Instant::now();
                map.retain(|_, entry| entry.expires_at > now);
            }
        });
    }

    pub fn get_or_insert<F>(&self, key: &str, ttl_secs: u64, compute: F) -> String
    where
        F: FnOnce() -> String,
    {
        // Check if key exists
        if let Some(value) = self.get(key) {
            return value;
        }

        // Compute the value
        let value = compute();

        // Insert it
        self.set(key.to_string(), value.clone(), ttl_secs);

        value
    }

    pub fn bulk_insert(&self, entries: Vec<(String, String, u64)>) {
        for (key, value, ttl) in entries {
            self.set(key, value, ttl);
        }
    }

    pub fn stats(&self) -> (usize, usize) {
        let map = self.data.lock().unwrap();
        let total = map.len();
        let now = Instant::now();
        let expired = map.values().filter(|e| e.expires_at < now).count();
        (total, expired)
    }
}

unsafe impl Send for Cache {}
unsafe impl Sync for Cache {}
