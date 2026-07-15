# Python Libraries for Data Engineering - Comprehensive Study Guide

## Table of Contents
1. [JSON Library](#json-library)
2. [Time Library](#time-library)
3. [Psycopg3 Library](#psycopg3-library)
4. [Multiprocessing Library](#multiprocessing-library)
5. [Threading Library](#threading-library)
6. [Selenium Library](#selenium-library)
7. [Pandas Library](#pandas-library)
8. [Asyncio Library](#asyncio-library)

---

## JSON Library

The JSON library is essential for data engineers as JSON is one of the most common data interchange formats. It provides methods to encode and decode JSON data, which is crucial when working with APIs, configuration files, and NoSQL databases.

### Core Methods and Functions

**json.dumps()** - Serializes Python objects to JSON strings
```python
import json

# Basic serialization
data = {"name": "John", "age": 30, "city": "New York"}
json_string = json.dumps(data)
print(json_string)  # {"name": "John", "age": 30, "city": "New York"}

# Pretty printing with indentation
pretty_json = json.dumps(data, indent=4)
print(pretty_json)

# Sorting keys alphabetically
sorted_json = json.dumps(data, sort_keys=True)
```

**json.loads()** - Deserializes JSON strings to Python objects
```python
json_string = '{"name": "John", "age": 30, "city": "New York"}'
data = json.loads(json_string)
print(data["name"])  # John
print(type(data))    # <class 'dict'>
```

**json.dump()** and **json.load()** - File operations
```python
# Writing to file
data = {"users": [{"id": 1, "name": "Alice"}, {"id": 2, "name": "Bob"}]}
with open("data.json", "w") as f:
    json.dump(data, f, indent=2)

# Reading from file
with open("data.json", "r") as f:
    loaded_data = json.load(f)
    print(loaded_data)
```

### Advanced Features and Parameters

**ensure_ascii** parameter controls ASCII encoding
```python
data = {"message": "HÃ©llo WÃ¶rld"}
# With ensure_ascii=True (default)
ascii_json = json.dumps(data)  # {"message": "H\\u00e9llo W\\u00f6rld"}

# With ensure_ascii=False
unicode_json = json.dumps(data, ensure_ascii=False)  # {"message": "HÃ©llo WÃ¶rld"}
```

**separators** parameter customizes output formatting
```python
data = {"a": 1, "b": 2}
compact_json = json.dumps(data, separators=(',', ':'))  # {"a":1,"b":2}
```

**default** parameter handles non-serializable objects
```python
from datetime import datetime

def datetime_handler(obj):
    if isinstance(obj, datetime):
        return obj.isoformat()
    raise TypeError(f"Object of type {type(obj)} is not JSON serializable")

data = {"timestamp": datetime.now(), "value": 42}
json_string = json.dumps(data, default=datetime_handler)
```

### Custom JSON Encoder and Decoder Classes

```python
class CustomEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return {"__datetime__": obj.isoformat()}
        if isinstance(obj, set):
            return {"__set__": list(obj)}
        return super().default(obj)

class CustomDecoder(json.JSONDecoder):
    def __init__(self):
        super().__init__(object_hook=self.object_hook)
    
    def object_hook(self, obj):
        if "__datetime__" in obj:
            return datetime.fromisoformat(obj["__datetime__"])
        if "__set__" in obj:
            return set(obj["__set__"])
        return obj

# Usage
data = {"timestamp": datetime.now(), "tags": {"python", "json"}}
json_string = json.dumps(data, cls=CustomEncoder)
decoded_data = json.loads(json_string, cls=CustomDecoder)
```

### Best Practices and Common Pitfalls

**Always handle JSON decode errors** when working with external data sources:
```python
def safe_json_load(json_string):
    try:
        return json.loads(json_string), None
    except json.JSONDecodeError as e:
        return None, f"JSON decode error: {e}"

data, error = safe_json_load('{"invalid": json}')
if error:
    print(f"Completed {len(results)} tasks successfully, {len(errors)} errors occurred")
    return results, errors

if __name__ == "__main__":
    results, errors = robust_multiprocessing()
```

### Best Practices and Common Pitfalls

**Always use `if __name__ == "__main__":` guard**
```python
# REQUIRED for multiprocessing on Windows and some Unix systems
if __name__ == "__main__":
    # Your multiprocessing code here
    pass
```

**Avoid sharing large objects between processes**
```python
# WRONG - inefficient pickling of large objects
def bad_approach():
    large_data = list(range(1000000))
    with mp.Pool() as pool:
        # This will pickle large_data for each worker
        results = pool.map(lambda x: process_item(x, large_data), range(100))

# BETTER - use shared memory or pass indices
def good_approach():
    large_data = list(range(1000000))
    
    def process_with_index(args):
        index, data_slice = args
        return process_item(index, data_slice)
    
    chunk_size = 1000
    chunks = [(i, large_data[i:i+chunk_size]) for i in range(0, len(large_data), chunk_size)]
    
    with mp.Pool() as pool:
        results = pool.map(process_with_index, chunks)
```

**Proper cleanup and resource management**
```python
def proper_cleanup_example():
    pool = None
    try:
        pool = mp.Pool(processes=4)
        results = pool.map(worker_function, range(10))
        return results
    except Exception as e:
        print(f"Error in multiprocessing: {e}")
        raise
    finally:
        if pool:
            pool.close()  # No more tasks
            pool.join()   # Wait for workers to finish
```

---

## Threading Library

### Conceptual Overview

Threading provides concurrency within a single process by allowing multiple threads to execute simultaneously, sharing the same memory space and resources. While Python's Global Interpreter Lock (GIL) prevents true parallel execution of CPU-bound tasks, threading excels at I/O-bound operations where threads can overlap waiting periods. For data engineers, this makes threading ideal for scenarios involving database connections, file operations, web API calls, and other tasks that spend time waiting for external resources.

The fundamental concept behind threading is cooperative multitasking within a shared memory space. All threads in a process share the same variables, objects, and resources, which enables efficient data sharing but requires careful synchronization to prevent race conditions and data corruption. Understanding when threading provides benefits versus when it creates problems is crucial for building effective data processing systems.

Threading becomes particularly valuable in data engineering when you're orchestrating multiple I/O operations: downloading data from multiple APIs simultaneously, reading from multiple databases concurrently, or processing files while simultaneously writing results to disk. The key insight is that while one thread waits for a network response or disk operation, other threads can continue working, dramatically improving overall throughput.

However, threading also introduces complexity around shared state management, deadlock prevention, and proper resource cleanup. Understanding these challenges and the synchronization primitives that address them is essential for building reliable concurrent data processing systems.

### Basic Threading Concepts

Threading operations revolve around creating thread objects, starting them, and coordinating their execution. The threading library provides both simple thread creation mechanisms and sophisticated synchronization tools for managing complex concurrent workflows.

**Thread Creation and Lifecycle Management**

Every thread has a lifecycle: creation, starting, execution, and termination. Understanding this lifecycle is crucial because improper thread management can lead to resource leaks, hanging processes, or unpredictable behavior in data pipelines.

```python
import threading
import time
import queue

def worker_thread(name, duration):
    """Basic worker function for demonstration"""
    print(f"Thread {name} starting")
    time.sleep(duration)
    print(f"Thread {name} completed after {duration} seconds")

def basic_threading():
    # Create threads
    thread1 = threading.Thread(target=worker_thread, args=("A", 2))
    thread2 = threading.Thread(target=worker_thread, args=("B", 3))
    
    # Start threads
    thread1.start()
    thread2.start()
    
    # Wait for completion
    thread1.join()
    thread2.join()
    
    print("All threads completed")
```

The `join()` method is crucial for thread coordination - it blocks the calling thread until the target thread completes. This ensures that your main program doesn't exit before worker threads finish their tasks, which is essential in data processing scripts where you need to ensure all data is processed before the program terminates.

**Thread Class Inheritance for Complex Workers**

For more sophisticated threading scenarios, inheriting from the Thread class provides better encapsulation and allows for more complex thread behavior. This approach is particularly useful in data engineering when you need threads that maintain state, handle multiple types of tasks, or implement complex processing logic.

```python
class WorkerThread(threading.Thread):
    def __init__(self, name, task_queue, result_queue):
        super().__init__()
        self.name = name
        self.task_queue = task_queue
        self.result_queue = result_queue
        self.daemon = True  # Dies when main thread dies
    
    def run(self):
        while True:
            try:
                task = self.task_queue.get(timeout=1)
                if task is None:
                    break
                
                # Process task
                result = self.process_task(task)
                self.result_queue.put(result)
                self.task_queue.task_done()
                
            except queue.Empty:
                continue
    
    def process_task(self, task):
        # Simulate processing
        time.sleep(0.1)
        return f"Processed {task} by {self.name}"
```

The `daemon` attribute is important for data processing applications - daemon threads automatically terminate when the main program exits, preventing hanging processes. The queue-based approach allows for dynamic work distribution and provides natural backpressure control.

**Thread-Safe Operations and Race Conditions**

Since threads share memory, they can interfere with each other when accessing shared data simultaneously. This creates race conditions where the final result depends on the unpredictable timing of thread execution. Locks provide mutual exclusion, ensuring that only one thread can access critical sections of code at a time.

```python
import threading
import time

class ThreadSafeCounter:
    def __init__(self):
        self._value = 0
        self._lock = threading.Lock()
    
    def increment(self):
        with self._lock:
            # Critical section - only one thread can execute this at a time
            current = self._value
            time.sleep(0.001)  # Simulate some work
            self._value = current + 1
    
    def get_value(self):
        with self._lock:
            return self._value
```

The `with self._lock:` context manager ensures that the lock is properly acquired and released, even if exceptions occur. Without this locking mechanism, multiple threads incrementing the counter simultaneously could read the same value and overwrite each other's updates, leading to lost increments and incorrect final values.

This pattern is fundamental in data engineering scenarios where multiple threads might be updating shared counters (like progress tracking), accumulating results, or maintaining shared data structures. The key principle is identifying critical sections - portions of code that must not be executed simultaneously by multiple threads.python
import threading
import time
import queue

def worker_thread(name, duration):
    """Basic worker function for demonstration"""
    print(f"Thread {name} starting")
    time.sleep(duration)
    print(f"Thread {name} completed after {duration} seconds")

def basic_threading():
    # Create threads
    thread1 = threading.Thread(target=worker_thread, args=("A", 2))
    thread2 = threading.Thread(target=worker_thread, args=("B", 3))
    
    # Start threads
    thread1.start()
    thread2.start()
    
    # Wait for completion
    thread1.join()
    thread2.join()
    
    print("All threads completed")

# Thread class inheritance approach
class WorkerThread(threading.Thread):
    def __init__(self, name, task_queue, result_queue):
        super().__init__()
        self.name = name
        self.task_queue = task_queue
        self.result_queue = result_queue
        self.daemon = True  # Dies when main thread dies
    
    def run(self):
        while True:
            try:
                task = self.task_queue.get(timeout=1)
                if task is None:
                    break
                
                # Process task
                result = self.process_task(task)
                self.result_queue.put(result)
                self.task_queue.task_done()
                
            except queue.Empty:
                continue
    
    def process_task(self, task):
        # Simulate processing
        time.sleep(0.1)
        return f"Processed {task} by {self.name}"
```

**Thread-safe operations with locks**
```python
import threading
import time

class ThreadSafeCounter:
    def __init__(self):
        self._value = 0
        self._lock = threading.Lock()
    
    def increment(self):
        with self._lock:
            # Critical section - only one thread can execute this at a time
            current = self._value
            time.sleep(0.001)  # Simulate some work
            self._value = current + 1
    
    def get_value(self):
        with self._lock:
            return self._value

def increment_worker(counter, num_increments):
    for _ in range(num_increments):
        counter.increment()

def demonstrate_thread_safety():
    counter = ThreadSafeCounter()
    threads = []
    
    # Create multiple threads that increment the counter
    for i in range(5):
        thread = threading.Thread(target=increment_worker, args=(counter, 100))
        threads.append(thread)
        thread.start()
    
    # Wait for all threads to complete
    for thread in threads:
        thread.join()
    
    print(f"Final counter value: {counter.get_value()}")  # Should be 500
```

### Advanced Threading Patterns

**Producer-Consumer pattern with Queue**
```python
import threading
import queue
import time
import random

def producer(q, producer_id, num_items):
    """Produces items and puts them in queue"""
    for i in range(num_items):
        item = f"Item-{producer_id}-{i}"
        q.put(item)
        print(f"Producer {producer_id} produced: {item}")
        time.sleep(random.uniform(0.01, 0.1))
    
    print(f"Producer {producer_id} finished")

def consumer(q, consumer_id):
    """Consumes items from queue"""
    consumed_items = []
    while True:
        try:
            item = q.get(timeout=2)
            consumed_items.append(item)
            print(f"Consumer {consumer_id} consumed: {item}")
            q.task_done()
            time.sleep(random.uniform(0.01, 0.05))
        except queue.Empty:
            print(f"Consumer {consumer_id} timed out")
            break
    
    return consumed_items

def producer_consumer_threading():
    # Create a queue with limited size
    q = queue.Queue(maxsize=10)
    
    # Create producer threads
    producers = []
    for i in range(2):
        producer_thread = threading.Thread(target=producer, args=(q, i, 10))
        producers.append(producer_thread)
        producer_thread.start()
    
    # Create consumer threads
    consumers = []
    for i in range(3):
        consumer_thread = threading.Thread(target=consumer, args=(q, i))
        consumers.append(consumer_thread)
        consumer_thread.start()
    
    # Wait for producers to finish
    for producer_thread in producers:
        producer_thread.join()
    
    # Wait for queue to be empty
    q.join()
    
    print("All items produced and consumed")
```

**Thread pool for managing multiple workers**
```python
from concurrent.futures import ThreadPoolExecutor, as_completed
import requests
import time

def fetch_url(url):
    """Fetch URL content - I/O bound operation perfect for threading"""
    try:
        response = requests.get(url, timeout=5)
        return {
            'url': url,
            'status_code': response.status_code,
            'content_length': len(response.content),
            'response_time': response.elapsed.total_seconds()
        }
    except Exception as e:
        return {
            'url': url,
            'error': str(e)
        }

def parallel_web_scraping():
    urls = [
        'https://httpbin.org/delay/1',
        'https://httpbin.org/delay/2',
        'https://httpbin.org/delay/1',
        'https://httpbin.org/json',
        'https://httpbin.org/headers'
    ]
    
    # Method 1: Using ThreadPoolExecutor with map
    with ThreadPoolExecutor(max_workers=3) as executor:
        results = list(executor.map(fetch_url, urls))
    
    for result in results:
        if 'error' in result:
            print(f"Error fetching {result['url']}: {result['error']}")
        else:
            print(f"Fetched {result['url']}: {result['status_code']} ({result['content_length']} bytes)")
    
    # Method 2: Using submit for more control
    with ThreadPoolExecutor(max_workers=3) as executor:
        # Submit all tasks
        future_to_url = {executor.submit(fetch_url, url): url for url in urls}
        
        # Process results as they complete
        for future in as_completed(future_to_url):
            url = future_to_url[future]
            try:
                result = future.result()
                print(f"Completed {url}")
            except Exception as e:
                print(f"Error processing {url}: {e}")

def data_processing_pipeline():
    """Threading pipeline for data processing"""
    import json
    
    # Simulate processing different types of data
    def process_json_data(data):
        time.sleep(0.1)  # Simulate processing time
        return json.loads(data) if isinstance(data, str) else data
    
    def validate_data(data):
        time.sleep(0.05)  # Simulate validation
        return data if isinstance(data, dict) and 'id' in data else None
    
    def save_data(data):
        time.sleep(0.2)  # Simulate database save
        return f"Saved record {data.get('id', 'unknown')}"
    
    # Sample data
    json_strings = [
        '{"id": 1, "name": "Alice", "age": 30}',
        '{"id": 2, "name": "Bob", "age": 25}',
        '{"id": 3, "name": "Charlie", "age": 35}',
        'invalid json',
        '{"id": 4, "name": "David", "age": 28}'
    ]
    
    with ThreadPoolExecutor(max_workers=4) as executor:
        # Stage 1: Parse JSON
        parsed_futures = [executor.submit(process_json_data, json_str) for json_str in json_strings]
        parsed_data = []
        for future in as_completed(parsed_futures):
            try:
                result = future.result()
                parsed_data.append(result)
            except Exception as e:
                print(f"JSON parsing error: {e}")
        
        # Stage 2: Validate data
        valid_futures = [executor.submit(validate_data, data) for data in parsed_data if data]
        valid_data = []
        for future in as_completed(valid_futures):
            result = future.result()
            if result:
                valid_data.append(result)
        
        # Stage 3: Save valid data
        save_futures = [executor.submit(save_data, data) for data in valid_data]
        for future in as_completed(save_futures):
            result = future.result()
            print(result)
```

### Synchronization Primitives

**Using different synchronization mechanisms**
```python
import threading
import time
import random

# Event for signaling between threads
def event_example():
    event = threading.Event()
    
    def waiter(name):
        print(f"{name} waiting for event...")
        event.wait()
        print(f"{name} received event!")
    
    def setter():
        time.sleep(2)
        print("Setting event")
        event.set()
    
    # Create threads
    waiters = [threading.Thread(target=waiter, args=(f"Waiter-{i}",)) for i in range(3)]
    setter_thread = threading.Thread(target=setter)
    
    # Start threads
    for w in waiters:
        w.start()
    setter_thread.start()
    
    # Wait for completion
    for w in waiters:
        w.join()
    setter_thread.join()

# Semaphore for limiting resource access
def semaphore_example():
    # Allow only 2 threads to access resource simultaneously
    semaphore = threading.Semaphore(2)
    
    def access_resource(worker_id):
        with semaphore:
            print(f"Worker {worker_id} acquired resource")
            time.sleep(random.uniform(1, 3))
            print(f"Worker {worker_id} released resource")
    
    threads = []
    for i in range(5):
        thread = threading.Thread(target=access_resource, args=(i,))
        threads.append(thread)
        thread.start()
    
    for thread in threads:
        thread.join()

# Condition for complex synchronization
def condition_example():
    condition = threading.Condition()
    items = []
    
    def consumer(name):
        with condition:
            while len(items) == 0:
                print(f"{name} waiting for items...")
                condition.wait()
            
            item = items.pop(0)
            print(f"{name} consumed {item}")
    
    def producer():
        for i in range(5):
            time.sleep(1)
            with condition:
                item = f"item-{i}"
                items.append(item)
                print(f"Produced {item}")
                condition.notify_all()  # Wake up all waiting consumers
    
    # Create threads
    consumers = [threading.Thread(target=consumer, args=(f"Consumer-{i}",)) for i in range(2)]
    producer_thread = threading.Thread(target=producer)
    
    # Start threads
    for c in consumers:
        c.start()
    producer_thread.start()
    
    # Wait for completion
    producer_thread.join()
    for c in consumers:
        c.join()
```

### Best Practices and Common Pitfalls

**Avoiding deadlocks with proper lock ordering**
```python
import threading

# WRONG - can cause deadlock
def deadlock_example():
    lock1 = threading.Lock()
    lock2 = threading.Lock()
    
    def thread1():
        with lock1:
            time.sleep(0.1)
            with lock2:  # Trying to acquire lock2 while holding lock1
                pass
    
    def thread2():
        with lock2:
            time.sleep(0.1)
            with lock1:  # Trying to acquire lock1 while holding lock2
                pass

# RIGHT - consistent lock ordering
def safe_locking():
    lock1 = threading.Lock()
    lock2 = threading.Lock()
    
    def thread1():
        with lock1:
            with lock2:  # Always acquire locks in the same order
                pass
    
    def thread2():
        with lock1:  # Same order as thread1
            with lock2:
                pass
```

**Proper exception handling in threads**
```python
import threading
import logging

def safe_worker_thread(task_queue, result_queue, error_callback=None):
    """Worker thread with proper exception handling"""
    while True:
        try:
            task = task_queue.get(timeout=1)
            if task is None:
                break
            
            # Process task
            result = process_task(task)
            result_queue.put(result)
            
        except queue.Empty:
            continue
        except Exception as e:
            error_msg = f"Error processing task: {e}"
            logging.error(error_msg)
            if error_callback:
                error_callback(e)
        finally:
            task_queue.task_done()

def process_task(task):
    # Your task processing logic
    if task == "error":
        raise ValueError("Simulated error")
    return f"Processed: {task}"
```

**Memory management and thread cleanup**
```python
class ManagedThreadPool:
    def __init__(self, max_workers=4):
        self.max_workers = max_workers
        self.threads = []
        self.task_queue = queue.Queue()
        self.shutdown_event = threading.Event()
    
    def start(self):
        for i in range(self.max_workers):
            thread = threading.Thread(target=self._worker, args=(i,))
            thread.daemon = True
            thread.start()
            self.threads.append(thread)
    
    def _worker(self, worker_id):
        while not self.shutdown_event.is_set():
            try:
                task = self.task_queue.get(timeout=1)
                if task is None:
                    break
                
                # Process task
                task()
                self.task_queue.task_done()
                
            except queue.Empty:
                continue
            except Exception as e:
                logging.error(f"Worker {worker_id} error: {e}")
    
    def submit(self, task):
        if not self.shutdown_event.is_set():
            self.task_queue.put(task)
    
    def shutdown(self, wait=True):
        self.shutdown_event.set()
        
        # Add termination signals for each worker
        for _ in self.threads:
            self.task_queue.put(None)
        
        if wait:
            for thread in self.threads:
                thread.join()
```

---

## Selenium Library

### Conceptual Overview

Selenium represents a paradigm shift from traditional web scraping to browser automation, providing the ability to interact with web pages exactly as a human user would. Unlike simple HTTP clients that can only retrieve static HTML, Selenium controls real web browsers (Chrome, Firefox, Safari, etc.), enabling interaction with dynamic JavaScript applications, single-page applications (SPAs), and complex web interfaces that generate content after page load.

For data engineers, Selenium becomes essential when dealing with modern web applications that heavily rely on JavaScript for content generation, require user interactions to reveal data, or implement anti-bot measures that defeat traditional scraping approaches. The library provides a programmatic interface to browser functionality, including clicking buttons, filling forms, scrolling pages, handling popups, and waiting for dynamic content to load.

The power of Selenium lies in its ability to execute JavaScript, handle AJAX requests, and interact with complex UI elements like dropdowns, modals, and infinite scroll interfaces. This makes it indispensable for extracting data from business intelligence dashboards, social media platforms, e-commerce sites with dynamic pricing, or any web application where the data is generated or modified by client-side code.

However, this power comes with complexity and performance overhead. Selenium operations are significantly slower than direct HTTP requests because they involve launching actual browsers, loading pages completely, and executing all JavaScript. Understanding when Selenium is necessary versus when simpler tools suffice is crucial for building efficient data extraction pipelines.

### Basic Setup and Browser Management

The foundation of any Selenium operation is proper browser setup and configuration. Modern web browsers offer extensive configuration options that affect performance, detection avoidance, and resource usage - all critical considerations for data engineering workflows.

**Understanding WebDriver Architecture and Browser Configuration**

WebDriver acts as a bridge between your Python code and the browser, translating high-level commands into browser-specific actions. Each browser requires its own driver (ChromeDriver for Chrome, GeckoDriver for Firefox), and proper configuration is essential for both functionality and performance.

```python
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
import time

def basic_selenium_setup():
    # Chrome options for headless operation
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run in background
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1080")
    
    # Initialize WebDriver
    driver = webdriver.Chrome(options=chrome_options)
    
    try:
        # Navigate to website
        driver.get("https://example.com")
        
        # Basic operations
        print(f"Title: {driver.title}")
        print(f"Current URL: {driver.current_url}")
        print(f"Page source length: {len(driver.page_source)}")
        
        # Take screenshot
        driver.save_screenshot("example_page.png")
        
    finally:
        driver.quit()  # Always close the browser
```

The `--headless` option runs the browser without a GUI, essential for server environments and automated pipelines. The `--no-sandbox` and `--disable-dev-shm-usage` options are often necessary in containerized environments where default browser security settings conflict with container restrictions. The window size setting ensures consistent rendering, which can affect how dynamic content loads.

**Advanced Browser Configuration for Production Use**

Production data extraction requires sophisticated browser configuration to balance performance, stealth, and reliability. Different scenarios call for different optimization strategies.

```python
def advanced_browser_configuration():
    """Advanced browser configuration for data scraping"""
    chrome_options = Options()
    
    # Performance optimizations
    chrome_options.add_argument("--disable-images")  # Don't load images
    chrome_options.add_argument("--disable-javascript")  # Disable JS if not needed
    chrome_options.add_argument("--disable-plugins")
    chrome_options.add_argument("--disable-extensions")
    
    # Stealth options to avoid detection
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    
    # Custom user agent
    chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
    
    driver = webdriver.Chrome(options=chrome_options)
    
    # Execute script to hide automation indicators
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    
    return driver
```

Each configuration option serves a specific purpose in data engineering contexts. Disabling images and JavaScript can significantly speed up page loads when you only need text content. Stealth options help avoid detection by websites that implement anti-bot measures. Custom user agents allow you to appear as different browser types or operating systems.

The post-initialization JavaScript execution removes telltale signs that the browser is being automated, which is important for accessing sites that actively detect and block automated access.

### Element Location and Interaction

**Finding elements using different strategies**
```python
def element_location_examples(driver):
    """Comprehensive examples of element location strategies"""
    
    # By ID - most reliable if available
    try:
        element = driver.find_element(By.ID, "username")
        element.send_keys("user@example.com")
    except:
        print("Element with ID 'username' not found")
    
    # By Class Name
    elements = driver.find_elements(By.CLASS_NAME, "product-item")
    print(f"Found {len(elements)} product items")
    
    # By CSS Selector - very flexible
    price_elements = driver.find_elements(By.CSS_SELECTOR, ".product .price")
    for price_elem in price_elements:
        print(f"Price: {price_elem.text}")
    
    # By XPath - most powerful but slower
    # Relative XPath (preferred)
    submit_button = driver.find_element(By.XPATH, "//button[@type='submit']")
    
    # XPath with text content
    link = driver.find_element(By.XPATH, "//a[contains(text(), 'Next Page')]")
    
    # XPath with multiple conditions
    specific_item = driver.find_element(
        By.XPATH, 
        "//div[@class='item' and @data-category='electronics']"
    )
    
    # By Tag Name - for generic elements
    all_links = driver.find_elements(By.TAG_NAME, "a")
    
    # By Name attribute
    search_input = driver.find_element(By.NAME, "search")
    
    # By Partial Link Text
    help_link = driver.find_element(By.PARTIAL_LINK_TEXT, "Help")

def wait_strategies():
    """Different waiting strategies for dynamic content"""
    driver = webdriver.Chrome()
    wait = WebDriverWait(driver, 10)
    
    try:
        # Wait for element to be present
        element = wait.until(
            EC.presence_of_element_located((By.ID, "dynamic-content"))
        )
        
        # Wait for element to be clickable
        button = wait.until(
            EC.element_to_be_clickable((By.ID, "submit-btn"))
        )
        button.click()
        
        # Wait for element to be visible
        result = wait.until(
            EC.visibility_of_element_located((By.CLASS_NAME, "result"))
        )
        
        # Wait for text to be present in element
        wait.until(
            EC.text_to_be_present_in_element((By.ID, "status"), "Complete")
        )
        
        # Wait for URL to contain specific text
        wait.until(EC.url_contains("success"))
        
        # Custom wait condition
        def custom_condition(driver):
            elements = driver.find_elements(By.CLASS_NAME, "item")
            return len(elements) > 5
        
        wait.until(custom_condition)
        
    finally:
        driver.quit()
```

### Advanced Interaction Patterns

**Handling forms, dropdowns, and complex interactions**
```python
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException, NoSuchElementException

def form_interactions(driver):
    """Advanced form handling"""
    
    # Text input with clearing existing content
    username_field = driver.find_element(By.ID, "username")
    username_field.clear()
    username_field.send_keys("testuser@example.com")
    
    # Password field
    password_field = driver.find_element(By.ID, "password")
    password_field.send_keys("securepassword123")
    
    # Dropdown selection
    dropdown = Select(driver.find_element(By.ID, "country"))
    dropdown.select_by_visible_text("United States")
    # Alternative methods:
    # dropdown.select_by_value("US")
    # dropdown.select_by_index(2)
    
    # Checkbox handling
    checkbox = driver.find_element(By.ID, "terms")
    if not checkbox.is_selected():
        checkbox.click()
    
    # Radio button selection
    radio_buttons = driver.find_elements(By.NAME, "payment_method")
    for radio in radio_buttons:
        if radio.get_attribute("value") == "credit_card":
            radio.click()
            break
    
    # File upload
    file_input = driver.find_element(By.ID, "file-upload")
    file_input.send_keys("/path/to/your/file.pdf")
    
    # Submit form
    submit_button = driver.find_element(By.XPATH, "//input[@type='submit']")
    submit_button.click()

def advanced_mouse_keyboard_actions(driver):
    """Complex mouse and keyboard interactions"""
    actions = ActionChains(driver)
    
    # Hover over element
    menu_item = driver.find_element(By.ID, "menu-item")
    actions.move_to_element(menu_item).perform()
    
    # Right-click (context menu)
    element = driver.find_element(By.ID, "context-menu-target")
    actions.context_click(element).perform()
    
    # Drag and drop
    source = driver.find_element(By.ID, "draggable")
    target = driver.find_element(By.ID, "droppable")
    actions.drag_and_drop(source, target).perform()
    
    # Complex action chain
    actions = ActionChains(driver)
    actions.move_to_element(menu_item)
    actions.click()
    actions.send_keys("search term")
    actions.send_keys(Keys.ENTER)
    actions.perform()
    
    # Keyboard shortcuts
    actions = ActionChains(driver)
    actions.key_down(Keys.CONTROL)
    actions.send_keys("a")  # Ctrl+A (select all)
    actions.key_up(Keys.CONTROL)
    actions.perform()

def handle_javascript_and_alerts(driver):
    """Handling JavaScript execution and alerts"""
    
    # Execute JavaScript
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    
    # Get return value from JavaScript
    page_height = driver.execute_script("return document.body.scrollHeight")
    print(f"Page height: {page_height}")
    
    # Inject JavaScript to modify page
    driver.execute_script("""
        var elements = document.getElementsByClassName('ad');
        for(var i = 0; i < elements.length; i++) {
            elements[i].style.display = 'none';
        }
    """)
    
    # Handle alerts
    try:
        # Trigger alert (example)
        driver.execute_script("alert('Test alert')")
        
        # Switch to alert and handle it
        alert = driver.switch_to.alert
        alert_text = alert.text
        print(f"Alert text: {alert_text}")
        alert.accept()  # or alert.dismiss() for cancel
        
    except:
        print("No alert present")
    
    # Handle confirm dialog
    driver.execute_script("confirm('Are you sure?')")
    confirm = driver.switch_to.alert
    confirm.accept()  # or confirm.dismiss()
    
    # Handle prompt dialog
    driver.execute_script("prompt('Enter your name:', 'Default')")
    prompt = driver.switch_to.alert
    prompt.send_keys("John Doe")
    prompt.accept()
```

### Web Scraping Patterns and Data Extraction

**Comprehensive web scraping example**
```python
import csv
import json
from datetime import datetime
import logging

class WebScraper:
    def __init__(self, headless=True, implicit_wait=10):
        self.setup_logging()
        self.driver = self.setup_driver(headless)
        self.driver.implicitly_wait(implicit_wait)
        self.wait = WebDriverWait(self.driver, 20)
    
    def setup_logging(self):
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
    
    def setup_driver(self, headless):
        options = Options()
        if headless:
            options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--window-size=1920,1080")
        
        return webdriver.Chrome(options=options)
    
    def scrape_ecommerce_products(self, base_url, max_pages=5):
        """Scrape product data from e-commerce site"""
        all_products = []
        
        for page in range(1, max_pages + 1):
            try:
                url = f"{base_url}?page={page}"
                self.logger.info(f"Scraping page {page}: {url}")
                
                self.driver.get(url)
                
                # Wait for products to load
                self.wait.until(
                    EC.presence_of_element_located((By.CLASS_NAME, "product-item"))
                )
                
                # Extract products from current page
                products = self.extract_products_from_page()
                all_products.extend(products)
                
                # Check if there's a next page
                if not self.has_next_page():
                    self.logger.info("No more pages available")
                    break
                
                # Random delay to be respectful
                time.sleep(random.uniform(1, 3))
                
            except TimeoutException:
                self.logger.error(f"Error extracting product: {e}")
                continue
        
        return products
    
    def parse_price(self, price_text):
        """Extract numeric price from price text"""
        import re
        price_match = re.search(r'[\d,]+\.?\d*', price_text.replace(',', ''))
        return float(price_match.group()) if price_match else None
    
    def parse_rating(self, rating_element):
        """Extract rating from rating element"""
        # Look for star rating or numeric rating
        rating_text = rating_element.text
        import re
        rating_match = re.search(r'(\d+\.?\d*)', rating_text)
        return float(rating_match.group()) if rating_match else None
    
    def has_next_page(self):
        """Check if there's a next page available"""
        try:
            next_button = self.driver.find_element(By.CLASS_NAME, "next-page")
            return next_button.is_enabled()
        except NoSuchElementException:
            return False
    
    def save_data(self, data, filename_base):
        """Save scraped data in multiple formats"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save as JSON
        json_filename = f"{filename_base}_{timestamp}.json"
        with open(json_filename, 'w') as f:
            json.dump(data, f, indent=2, default=str)
        
        # Save as CSV
        if data:
            csv_filename = f"{filename_base}_{timestamp}.csv"
            with open(csv_filename, 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=data[0].keys())
                writer.writeheader()
                writer.writerows(data)
        
        self.logger.info(f"Saved {len(data)} records to {json_filename} and {csv_filename}")
    
    def close(self):
        """Clean up resources"""
        if self.driver:
            self.driver.quit()

# Usage example
def run_scraping_job():
    scraper = WebScraper(headless=True)
    try:
        products = scraper.scrape_ecommerce_products("https://example-shop.com/products", max_pages=3)
        scraper.save_data(products, "scraped_products")
        print(f"Scraped {len(products)} products successfully")
    finally:
        scraper.close()
```

### Handling Dynamic Content and SPAs

**Working with Single Page Applications and AJAX**
```python
def handle_dynamic_content(driver):
    """Handle dynamically loaded content"""
    
    # Wait for AJAX requests to complete
    def wait_for_ajax(driver):
        wait = WebDriverWait(driver, 10)
        try:
            wait.until(lambda driver: driver.execute_script("return jQuery.active == 0"))
        except:
            # Fallback if jQuery is not available
            time.sleep(2)
    
    # Infinite scroll handling
    def scroll_to_load_content(driver, max_scrolls=10):
        """Handle infinite scroll pages"""
        last_height = driver.execute_script("return document.body.scrollHeight")
        scrolls = 0
        
        while scrolls < max_scrolls:
            # Scroll to bottom
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            
            # Wait for new content to load
            time.sleep(2)
            
            # Check if new content loaded
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            
            last_height = new_height
            scrolls += 1
        
        return scrolls
    
    # Handle lazy-loaded images
    def load_all_images(driver):
        """Trigger loading of lazy-loaded images"""
        images = driver.find_elements(By.TAG_NAME, "img")
        for img in images:
            driver.execute_script("arguments[0].scrollIntoView();", img)
            time.sleep(0.1)
    
    # Wait for specific content to appear
    def wait_for_content_update(driver, locator, expected_count):
        """Wait for specific number of elements to appear"""
        wait = WebDriverWait(driver, 30)
        wait.until(lambda d: len(d.find_elements(*locator)) >= expected_count)

def handle_spa_navigation(driver):
    """Navigate Single Page Applications"""
    
    # Click navigation without page refresh
    nav_link = driver.find_element(By.LINK_TEXT, "Products")
    nav_link.click()
    
    # Wait for URL change (SPA navigation)
    WebDriverWait(driver, 10).until(EC.url_contains("products"))
    
    # Wait for content to load after navigation
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, "product-list"))
    )
    
    # Handle browser back/forward in SPA
    driver.back()
    time.sleep(1)
    driver.forward()

def extract_data_from_tables(driver):
    """Extract structured data from HTML tables"""
    
    # Find table
    table = driver.find_element(By.TAG_NAME, "table")
    
    # Extract headers
    headers = []
    header_cells = table.find_elements(By.TAG_NAME, "th")
    for cell in header_cells:
        headers.append(cell.text.strip())
    
    # Extract rows
    rows_data = []
    rows = table.find_elements(By.TAG_NAME, "tr")[1:]  # Skip header row
    
    for row in rows:
        cells = row.find_elements(By.TAG_NAME, "td")
        row_data = {}
        for i, cell in enumerate(cells):
            if i < len(headers):
                row_data[headers[i]] = cell.text.strip()
        rows_data.append(row_data)
    
    return rows_data
```

### Best Practices and Performance Optimization

**Error handling and robust scraping**
```python
from selenium.common.exceptions import (
    TimeoutException, NoSuchElementException, ElementClickInterceptedException,
    StaleElementReferenceException, WebDriverException
)

class RobustScraper:
    def __init__(self):
        self.setup_driver()
        self.max_retries = 3
        self.retry_delay = 2
    
    def robust_find_element(self, by, value, timeout=10):
        """Find element with retry logic"""
        for attempt in range(self.max_retries):
            try:
                wait = WebDriverWait(self.driver, timeout)
                element = wait.until(EC.presence_of_element_located((by, value)))
                return element
            except TimeoutException:
                if attempt == self.max_retries - 1:
                    raise
                time.sleep(self.retry_delay)
    
    def safe_click(self, element):
        """Click element with retry logic for common issues"""
        for attempt in range(self.max_retries):
            try:
                # Scroll element into view
                self.driver.execute_script("arguments[0].scrollIntoView(true);", element)
                time.sleep(0.5)
                
                # Wait for element to be clickable
                wait = WebDriverWait(self.driver, 10)
                wait.until(EC.element_to_be_clickable(element))
                
                # Click the element
                element.click()
                return True
                
            except ElementClickInterceptedException:
                # Try JavaScript click as fallback
                try:
                    self.driver.execute_script("arguments[0].click();", element)
                    return True
                except:
                    pass
            
            except StaleElementReferenceException:
                # Re-find the element
                return False
            
            except Exception as e:
                if attempt == self.max_retries - 1:
                    raise e
                time.sleep(self.retry_delay)
        
        return False
    
    def safe_get_text(self, element):
        """Safely extract text from element"""
        try:
            return element.text.strip()
        except StaleElementReferenceException:
            return None
        except Exception:
            return None
    
    def handle_popups_and_overlays(self):
        """Handle common popup elements that might interfere"""
        popup_selectors = [
            "//button[contains(text(), 'Accept')]",
            "//button[contains(text(), 'Close')]",
            "//*[@class='modal-close']",
            "//*[@class='popup-close']",
            "//div[contains(@class, 'cookie')]//button"
        ]
        
        for selector in popup_selectors:
            try:
                popup = self.driver.find_element(By.XPATH, selector)
                if popup.is_displayed():
                    popup.click()
                    time.sleep(1)
            except:
                continue

def performance_optimizations():
    """Various performance optimization techniques"""
    
    # Disable images and CSS for faster loading
    chrome_options = Options()
    prefs = {
        "profile.managed_default_content_settings.images": 2,  # Block images
        "profile.default_content_setting_values.notifications": 2,  # Block notifications
        "profile.managed_default_content_settings.stylesheets": 2,  # Block CSS
    }
    chrome_options.add_experimental_option("prefs", prefs)
    
    # Use headless mode for faster execution
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    
    # Optimize for data scraping
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--disable-plugins")
    
    driver = webdriver.Chrome(options=chrome_options)
    
    # Set page load timeout
    driver.set_page_load_timeout(30)
    
    # Set script timeout
    driver.set_script_timeout(30)
    
    return driver

def concurrent_scraping_example():
    """Example of concurrent scraping with threading"""
    import threading
    import queue
    
    def worker_scraper(url_queue, result_queue):
        driver = performance_optimizations()
        try:
            while True:
                try:
                    url = url_queue.get(timeout=5)
                    if url is None:
                        break
                    
                    # Scrape the URL
                    driver.get(url)
                    title = driver.title
                    result_queue.put({'url': url, 'title': title})
                    url_queue.task_done()
                    
                except queue.Empty:
                    break
                except Exception as e:
                    result_queue.put({'url': url, 'error': str(e)})
                    url_queue.task_done()
        finally:
            driver.quit()
    
    # URLs to scrape
    urls = [f"https://example.com/page/{i}" for i in range(1, 11)]
    
    # Create queues
    url_queue = queue.Queue()
    result_queue = queue.Queue()
    
    # Add URLs to queue
    for url in urls:
        url_queue.put(url)
    
    # Create worker threads
    num_workers = 3
    threads = []
    for i in range(num_workers):
        thread = threading.Thread(target=worker_scraper, args=(url_queue, result_queue))
        thread.start()
        threads.append(thread)
    
    # Signal workers to stop
    for _ in range(num_workers):
        url_queue.put(None)
    
    # Wait for completion
    for thread in threads:
        thread.join()
    
    # Collect results
    results = []
    while not result_queue.empty():
        results.append(result_queue.get())
    
    return results
```

### Common Pitfalls and Solutions

**Avoiding detection and handling anti-bot measures**
```python
def stealth_scraping_setup():
    """Setup browser to avoid detection"""
    chrome_options = Options()
    
    # Stealth options
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    
    # Rotate user agents
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    ]
    
    import random
    chrome_options.add_argument(f"--user-agent={random.choice(user_agents)}")
    
    driver = webdriver.Chrome(options=chrome_options)
    
    # Execute stealth scripts
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    driver.execute_script("Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]})")
    driver.execute_script("Object.defineProperty(navigator, 'languages', {get: () => ['en-US', 'en']})")
    
    return driver

def respectful_scraping_practices():
    """Implement respectful scraping practices"""
    
    # Random delays between requests
    import random
    
    def random_delay(min_delay=1, max_delay=3):
        time.sleep(random.uniform(min_delay, max_delay))
    
    # Respect robots.txt (check manually or use robotparser)
    def check_robots_txt(base_url, user_agent="*"):
        import urllib.robotparser
        try:
            rp = urllib.robotparser.RobotFileParser()
            rp.set_url(f"{base_url}/robots.txt")
            rp.read()
            return rp.can_fetch(user_agent, base_url)
        except:
            return True  # If can't check, assume allowed
    
    # Implement rate limiting
    class RateLimiter:
        def __init__(self, max_requests_per_minute=30):
            self.max_requests = max_requests_per_minute
            self.requests = []
        
        def wait_if_needed(self):
            now = time.time()
            # Remove requests older than 1 minute
            self.requests = [req_time for req_time in self.requests if now - req_time < 60]
            
            if len(self.requests) >= self.max_requests:
                sleep_time = 60 - (now - self.requests[0])
                if sleep_time > 0:
                    time.sleep(sleep_time)
            
            self.requests.append(now)
    
    return RateLimiter()
```

---

## Pandas Library

Pandas is the cornerstone library for data manipulation and analysis in Python. It provides powerful data structures and data analysis tools that are essential for any data engineering workflow, from data cleaning to complex transformations.

### Core Data Structures

**DataFrame and Series fundamentals**
```python
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def dataframe_basics():
    """Understanding DataFrames and Series"""
    
    # Creating DataFrames from different sources
    # From dictionary
    data = {
        'name': ['Alice', 'Bob', 'Charlie', 'Diana'],
        'age': [25, 30, 35, 28],
        'city': ['New York', 'London', 'Tokyo', 'Paris'],
        'salary': [70000, 80000, 90000, 75000]
    }
    df = pd.DataFrame(data)
    
    # From list of dictionaries
    records = [
        {'name': 'Alice', 'age': 25, 'city': 'New York'},
        {'name': 'Bob', 'age': 30, 'city': 'London'},
        {'name': 'Charlie', 'age': 35, 'city': 'Tokyo'}
    ]
    df_from_records = pd.DataFrame.from_records(records)
    
    # From numpy array with custom columns
    np_data = np.random.rand(5, 3)
    df_from_numpy = pd.DataFrame(np_data, columns=['A', 'B', 'C'])
    
    # Series creation and operations
    ages = pd.Series([25, 30, 35, 28], name='age')
    names = pd.Series(['Alice', 'Bob', 'Charlie', 'Diana'], name='name')
    
    # Series with custom index
    prices = pd.Series([100, 200, 150], index=['AAPL', 'GOOGL', 'MSFT'], name='stock_price')
    
    # Basic DataFrame information
    print("DataFrame shape:", df.shape)
    print("DataFrame info:")
    print(df.info())
    print("DataFrame describe:")
    print(df.describe())
    print("DataFrame dtypes:")
    print(df.dtypes)
    
    return df

def indexing_and_selection():
    """Advanced indexing and selection techniques"""
    
    # Create sample data
    df = pd.DataFrame({
        'A': range(10),
        'B': range(10, 20),
        'C': range(20, 30),
        'D': ['X' if i % 2 == 0 else 'Y' for i in range(10)]
    })
    
    # Label-based indexing with .loc
    print("Single row by index:")
    print(df.loc[0])
    
    print("Multiple rows by index:")
    print(df.loc[0:2])  # Inclusive of end
    
    print("Specific rows and columns:")
    print(df.loc[0:2, 'A':'C'])  # Inclusive of end column
    
    print("Boolean indexing with .loc:")
    print(df.loc[df['A'] > 5, ['A', 'C']])
    
    # Position-based indexing with .iloc
    print("First 3 rows, first 2 columns:")
    print(df.iloc[0:3, 0:2])  # Exclusive of end
    
    print("Last 2 rows:")
    print(df.iloc[-2:])
    
    print("Every other row:")
    print(df.iloc[::2])
    
    # Advanced boolean indexing
    print("Multiple conditions:")
    condition = (df['A'] > 3) & (df['B'] < 18)
    print(df[condition])
    
    print("Using isin() method:")
    print(df[df['D'].isin(['X'])])
    
    # Query method for complex conditions
    print("Using query method:")
    result = df.query("A > 5 and B < 18")
    print(result)
    
    return df
```

### Data Import/Export Operations

**Reading and writing data from various sources**
```python
def data_io_operations():
    """Comprehensive data input/output operations"""
    
    # CSV operations with various parameters
    def csv_operations():
        # Reading CSV with advanced options
        df = pd.read_csv(
            'data.csv',
            sep=',',
            header=0,
            index_col=0,
            usecols=['name', 'age', 'salary'],
            dtype={'age': int, 'salary': float},
            parse_dates=['hire_date'],
            na_values=['N/A', 'NULL', ''],
            skiprows=1,
            nrows=1000,
            encoding='utf-8'
        )
        
        # Writing CSV with options
        df.to_csv(
            'output.csv',
            index=False,
            sep='|',
            na_rep='NULL',
            date_format='%Y-%m-%d',
            float_format='%.2f'
        )
    
    # Excel operations
    def excel_operations():
        # Reading Excel with multiple sheets
        excel_file = pd.ExcelFile('data.xlsx')
        sheet_names = excel_file.sheet_names
        
        # Read specific sheet
        df = pd.read_excel('data.xlsx', sheet_name='Sheet1')
        
        # Read multiple sheets
        all_sheets = pd.read_excel('data.xlsx', sheet_name=None)
        
        # Writing to Excel with multiple sheets
        with pd.ExcelWriter('output.xlsx', engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Data', index=False)
            df.describe().to_excel(writer, sheet_name='Summary')
    
    # JSON operations
    def json_operations():
        # Read JSON
        df = pd.read_json('data.json', orient='records')
        
        # Write JSON
        df.to_json('output.json', orient='records', date_format='iso')
        
        # Handle nested JSON
        with open('nested_data.json') as f:
            import json
            data = json.load(f)
            df = pd.json_normalize(data, sep='_')
    
    # Database operations
    def database_operations():
        import sqlite3
        from sqlalchemy import create_engine
        
        # SQLite connection
        conn = sqlite3.connect('database.db')
        df = pd.read_sql_query("SELECT * FROM table_name", conn)
        df.to_sql('new_table', conn, if_exists='replace', index=False)
        conn.close()
        
        # Using SQLAlchemy for other databases
        engine = create_engine('postgresql://user:pass@localhost/db')
        df = pd.read_sql('SELECT * FROM employees', engine)
        df.to_sql('processed_employees', engine, if_exists='append')
    
    # Parquet operations (efficient for large datasets)
    def parquet_operations():
        # Read Parquet
        df = pd.read_parquet('data.parquet')
        
        # Write Parquet with compression
        df.to_parquet('output.parquet', compression='snappy', index=False)
        
        # Read specific columns
        df_subset = pd.read_parquet('data.parquet', columns=['name', 'age'])
    
    return "Data I/O operations completed"

def data_cleaning_and_preprocessing():
    """Comprehensive data cleaning operations"""
    
    # Create sample data with various issues
    data = {
        'name': ['Alice', 'Bob', '', 'Diana', 'Eve', None],
        'age': [25, 30, np.nan, 28, 35, 22],
        'salary': [70000, 80000, 90000, np.nan, 85000, 60000],
        'email': ['alice@email.com', 'BOB@EMAIL.COM', 'charlie@', 'diana@email.com', '', 'eve@email.com'],
        'phone': ['123-456-7890', '(234) 567-8901', '345.678.9012', '456 789 0123', '567-890-1234', ''],
        'date_joined': ['2023-01-15', '2023/02/20', '15-03-2023', '2023-04-10', 'invalid', '2023-05-25']
    }
    df = pd.DataFrame(data)
    
    print("Original data:")
    print(df)
    print(f"Shape: {df.shape}")
    print(f"Null values:\n{df.isnull().sum()}")
    
    # Handle missing values
    def handle_missing_values(df):
        # Identify missing values
        print("Missing value patterns:")
        print(df.isnull().sum())
        
        # Drop rows with any null values
        df_dropna = df.dropna()
        
        # Drop rows where specific columns are null
        df_dropna_subset = df.dropna(subset=['name', 'age'])
        
        # Fill missing values
        df_filled = df.copy()
        df_filled['age'].fillna(df_filled['age'].mean(), inplace=True)
        df_filled['salary'].fillna(df_filled['salary'].median(), inplace=True)
        df_filled['name'].fillna('Unknown', inplace=True)
        
        # Forward fill and backward fill
        df_filled['email'].fillna(method='ffill', inplace=True)
        df_filled['phone'].fillna(method='bfill', inplace=True)
        
        return df_filled
    
    # Data type conversions
    def convert_data_types(df):
        df_converted = df.copy()
        
        # Convert numeric columns
        df_converted['age'] = pd.to_numeric(df_converted['age'], errors='coerce')
        df_converted['salary'] = pd.to_numeric(df_converted['salary'], errors='coerce')
        
        # Convert string columns
        df_converted['name'] = df_converted['name'].astype(str)
        df_converted['email'] = df_converted['email'].astype(str).str.lower().str.strip()
        
        # Convert date columns
        df_converted['date_joined'] = pd.to_datetime(df_converted['date_joined'], errors='coerce')
        
        return df_converted
    
    # String cleaning operations
    def clean_string_data(df):
        df_clean = df.copy()
        
        # Clean email addresses
        df_clean['email'] = df_clean['email'].str.lower().str.strip()
        df_clean['email'] = df_clean['email'].replace('', np.nan)
        
        # Standardize phone numbers
        df_clean['phone_clean'] = (df_clean['phone']
                                   .str.replace(r'[^\d]', '', regex=True)
                                   .str.replace(r'^(\d{3})(\d{3})(\d{4})f"Timeout on page {page}")
                continue
            except Exception as e:
                self.logger.error(f"Error on page {page}: {e}")
                continue
        
        return all_products
    
    def extract_products_from_page(self):
        """Extract product information from current page"""
        products = []
        product_elements = self.driver.find_elements(By.CLASS_NAME, "product-item")
        
        for element in product_elements:
            try:
                product = {}
                
                # Product name
                name_elem = element.find_element(By.CLASS_NAME, "product-name")
                product['name'] = name_elem.text.strip()
                
                # Price
                price_elem = element.find_element(By.CLASS_NAME, "price")
                price_text = price_elem.text.strip()
                product['price'] = self.parse_price(price_text)
                
                # Rating
                try:
                    rating_elem = element.find_element(By.CLASS_NAME, "rating")
                    product['rating'] = self.parse_rating(rating_elem)
                except NoSuchElementException:
                    product['rating'] = None
                
                # Product URL
                link_elem = element.find_element(By.TAG_NAME, "a")
                product['url'] = link_elem.get_attribute("href")
                
                # Image URL
                try:
                    img_elem = element.find_element(By.TAG_NAME, "img")
                    product['image_url'] = img_elem.get_attribute("src")
                except NoSuchElementException:
                    product['image_url'] = None
                
                # Availability
                try:
                    stock_elem = element.find_element(By.CLASS_NAME, "stock-status")
                    product['in_stock'] = "in stock" in stock_elem.text.lower()
                except NoSuchElementException:
                    product['in_stock'] = True  # Assume in stock if not specified
                
                product['scraped_at'] = datetime.now().isoformat()
                products.append(product)
                
            except Exception as e:
                self.logger.error(Failed to parse JSON: {error}")
```

**Be careful with floating-point precision** in JSON:
```python
import decimal

# Problem: floating point precision loss
data = {"price": 19.99}
json_string = json.dumps(data)
loaded = json.loads(json_string)
print(loaded["price"] == 19.99)  # Might be False due to floating point

# Solution: use parse_float parameter
loaded_decimal = json.loads(json_string, parse_float=decimal.Decimal)
```

**Memory considerations for large JSON files**:
```python
import ijson  # Third-party library for streaming JSON

# Instead of loading entire file into memory
def process_large_json_stream(filename):
    with open(filename, 'rb') as f:
        # Parse items one by one
        for item in ijson.items(f, 'users.item'):
            yield item
```

---

## Time Library

The time library provides various time-related functions essential for data engineering tasks like timestamping, scheduling, performance measurement, and working with different time zones.

### Core Functions

**time.time()** - Returns current Unix timestamp as float
```python
import time

current_timestamp = time.time()
print(current_timestamp)  # e.g., 1693834567.123456

# Common use case: measuring execution time
start_time = time.time()
# Some operation here
time.sleep(1)
end_time = time.time()
execution_time = end_time - start_time
print(f"Operation took {execution_time:.2f} seconds")
```

**time.sleep()** - Pauses execution for specified seconds
```python
# Basic sleep
time.sleep(2)  # Sleep for 2 seconds

# Sleep with fractional seconds
time.sleep(0.5)  # Sleep for 500 milliseconds

# Use in retry logic
def retry_operation(func, max_attempts=3, delay=1):
    for attempt in range(max_attempts):
        try:
            return func()
        except Exception as e:
            if attempt == max_attempts - 1:
                raise e
            print(f"Attempt {attempt + 1} failed, retrying in {delay} seconds...")
            time.sleep(delay)
            delay *= 2  # Exponential backoff
```

**time.strftime()** and **time.strptime()** - String formatting and parsing
```python
# Current time formatting
current_time = time.time()
formatted_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(current_time))
print(formatted_time)  # 2023-09-04 14:30:15

# Parsing time strings
time_string = "2023-09-04 14:30:15"
parsed_time = time.strptime(time_string, "%Y-%m-%d %H:%M:%S")
print(parsed_time)  # time.struct_time object

# Convert back to timestamp
timestamp = time.mktime(parsed_time)
```

**time.localtime()** and **time.gmtime()** - Convert timestamps to struct_time
```python
timestamp = time.time()

# Local time
local_time = time.localtime(timestamp)
print(f"Local time: {local_time}")

# UTC time
utc_time = time.gmtime(timestamp)
print(f"UTC time: {utc_time}")

# Access individual components
print(f"Year: {local_time.tm_year}")
print(f"Month: {local_time.tm_mon}")
print(f"Day: {local_time.tm_mday}")
```

### Advanced Time Operations

**Performance measurement with time.perf_counter()**
```python
# More precise than time.time() for performance measurement
def measure_performance(func, *args, **kwargs):
    start = time.perf_counter()
    result = func(*args, **kwargs)
    end = time.perf_counter()
    print(f"Function executed in {end - start:.6f} seconds")
    return result

def slow_operation():
    time.sleep(0.1)
    return "completed"

result = measure_performance(slow_operation)
```

**Working with time zones using time.timezone**
```python
# Get timezone information
print(f"Local timezone offset: {time.timezone} seconds")
print(f"Daylight saving time: {time.daylight}")
print(f"Timezone names: {time.tzname}")

# Better approach: use datetime module with pytz for timezone handling
from datetime import datetime, timezone
import pytz

# Create timezone-aware timestamps
utc_now = datetime.now(timezone.utc)
eastern = pytz.timezone('US/Eastern')
eastern_now = utc_now.astimezone(eastern)
```

**Creating time-based file names and logging**
```python
def create_timestamped_filename(base_name, extension="txt"):
    timestamp = time.strftime("%Y%m%d_%H%M%S", time.localtime())
    return f"{base_name}_{timestamp}.{extension}"

# Usage
log_file = create_timestamped_filename("data_processing", "log")
print(log_file)  # data_processing_20230904_143015.log
```

### Best Practices and Common Pitfalls

**Always use UTC for data storage and processing**:
```python
# Good: Store UTC timestamps
def get_utc_timestamp():
    return time.time()  # Always UTC

# Good: Convert to local time only for display
def display_local_time(utc_timestamp):
    local_time = time.localtime(utc_timestamp)
    return time.strftime("%Y-%m-%d %H:%M:%S %Z", local_time)
```

**Be careful with daylight saving time transitions**:
```python
# Problem: time.mktime() can be ambiguous during DST transitions
# Solution: Use datetime module with timezone support

from datetime import datetime, timezone

def safe_timestamp_conversion(dt_string, tz=timezone.utc):
    dt = datetime.fromisoformat(dt_string).replace(tzinfo=tz)
    return dt.timestamp()
```

**Avoid using time.sleep() in production code for precise timing**:
```python
# Instead of time.sleep() for precise intervals
import threading

def precise_timer(interval, func, *args, **kwargs):
    def run():
        threading.Timer(interval, func, args, kwargs).start()
    return run
```

---

## Psycopg3 Library

Psycopg3 is the modern Python adapter for PostgreSQL databases, providing both synchronous and asynchronous interfaces. It's essential for data engineers working with PostgreSQL databases for ETL processes, data warehousing, and analytics.

### Basic Connection and Operations

**Establishing connections**
```python
import psycopg
from psycopg import sql

# Basic connection
conn = psycopg.connect("postgresql://user:password@localhost:5432/database")

# Using connection parameters
conn = psycopg.connect(
    host="localhost",
    port=5432,
    user="postgres",
    password="password",
    dbname="mydb"
)

# Connection with SSL and additional parameters
conn = psycopg.connect(
    host="production-db.example.com",
    port=5432,
    user="app_user",
    password="secure_password",
    dbname="analytics",
    sslmode="require",
    connect_timeout=10,
    application_name="data_pipeline"
)
```

**Basic CRUD operations**
```python
# Using context manager for automatic cleanup
with psycopg.connect("postgresql://user:pass@localhost/db") as conn:
    with conn.cursor() as cur:
        # INSERT operation
        cur.execute(
            "INSERT INTO users (name, email, age) VALUES (%s, %s, %s)",
            ("John Doe", "john@example.com", 30)
        )
        
        # SELECT operation
        cur.execute("SELECT * FROM users WHERE age > %s", (25,))
        results = cur.fetchall()
        for row in results:
            print(f"Name: {row[1]}, Email: {row[2]}, Age: {row[3]}")
        
        # UPDATE operation
        cur.execute(
            "UPDATE users SET age = %s WHERE name = %s",
            (31, "John Doe")
        )
        
        # DELETE operation
        cur.execute("DELETE FROM users WHERE age < %s", (18,))
        
        # Commit all changes
        conn.commit()
```

**Working with different fetch methods**
```python
with psycopg.connect(conn_string) as conn:
    with conn.cursor() as cur:
        cur.execute("SELECT id, name, salary FROM employees ORDER BY salary DESC")
        
        # Fetch one row at a time
        first_row = cur.fetchone()
        print(f"Highest paid: {first_row}")
        
        # Fetch multiple rows
        next_five = cur.fetchmany(5)
        for row in next_five:
            print(f"Employee: {row[1]}, Salary: {row[2]}")
        
        # Fetch all remaining rows
        remaining = cur.fetchall()
        print(f"Remaining employees: {len(remaining)}")
```

### Advanced Database Operations

**Working with transactions and error handling**
```python
def transfer_funds(conn, from_account, to_account, amount):
    try:
        with conn.cursor() as cur:
            # Start transaction (implicit)
            
            # Check source account balance
            cur.execute(
                "SELECT balance FROM accounts WHERE account_id = %s FOR UPDATE",
                (from_account,)
            )
            balance = cur.fetchone()
            if not balance or balance[0] < amount:
                raise ValueError("Insufficient funds")
            
            # Debit source account
            cur.execute(
                "UPDATE accounts SET balance = balance - %s WHERE account_id = %s",
                (amount, from_account)
            )
            
            # Credit destination account
            cur.execute(
                "UPDATE accounts SET balance = balance + %s WHERE account_id = %s",
                (amount, to_account)
            )
            
            # Log transaction
            cur.execute(
                """INSERT INTO transaction_log (from_account, to_account, amount, timestamp)
                   VALUES (%s, %s, %s, NOW())""",
                (from_account, to_account, amount)
            )
            
            # Commit transaction
            conn.commit()
            print(f"Transfer of ${amount} completed successfully")
            
    except Exception as e:
        # Rollback on any error
        conn.rollback()
        print(f"Transfer failed: {e}")
        raise
```

**Bulk operations and batch processing**
```python
def bulk_insert_users(conn, users_data):
    with conn.cursor() as cur:
        # Method 1: executemany for multiple single inserts
        cur.executemany(
            "INSERT INTO users (name, email, department) VALUES (%s, %s, %s)",
            users_data
        )
        
        # Method 2: COPY for very large datasets (most efficient)
        with cur.copy("COPY users (name, email, department) FROM STDIN") as copy:
            for user in users_data:
                copy.write_row(user)
        
        conn.commit()

# Usage
users = [
    ("Alice Johnson", "alice@company.com", "Engineering"),
    ("Bob Smith", "bob@company.com", "Marketing"),
    ("Carol Davis", "carol@company.com", "Sales")
]
bulk_insert_users(conn, users)
```

**Dynamic query building with sql module**
```python
from psycopg import sql

def build_dynamic_query(table_name, columns, conditions):
    # Safely build dynamic queries
    query = sql.SQL("SELECT {columns} FROM {table} WHERE {conditions}").format(
        columns=sql.SQL(", ").join(map(sql.Identifier, columns)),
        table=sql.Identifier(table_name),
        conditions=sql.SQL(" AND ").join([
            sql.SQL("{} = %s").format(sql.Identifier(col))
            for col in conditions.keys()
        ])
    )
    return query, list(conditions.values())

# Usage
columns = ["id", "name", "salary"]
conditions = {"department": "Engineering", "active": True}
query, params = build_dynamic_query("employees", columns, conditions)

with conn.cursor() as cur:
    cur.execute(query, params)
    results = cur.fetchall()
```

### Connection Pooling and Management

**Using connection pools for production applications**
```python
from psycopg_pool import ConnectionPool

# Create a connection pool
pool = ConnectionPool(
    conninfo="postgresql://user:pass@localhost/db",
    min_size=5,
    max_size=20,
    max_waiting=10,
    max_idle=300,  # seconds
    num_workers=3
)

def process_data_batch(batch_data):
    with pool.connection() as conn:
        with conn.cursor() as cur:
            for item in batch_data:
                cur.execute(
                    "INSERT INTO processed_data (data, processed_at) VALUES (%s, NOW())",
                    (item,)
                )
            conn.commit()

# Use the pool in your application
data_batches = [["data1", "data2"], ["data3", "data4"]]
for batch in data_batches:
    process_data_batch(batch)

# Close pool when done
pool.close()
```

**Monitoring and health checks**
```python
def check_database_health(conn):
    try:
        with conn.cursor() as cur:
            # Check basic connectivity
            cur.execute("SELECT 1")
            cur.fetchone()
            
            # Check specific table accessibility
            cur.execute("SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public'")
            table_count = cur.fetchone()[0]
            
            # Check database size
            cur.execute("""
                SELECT pg_size_pretty(pg_database_size(current_database())) as size
            """)
            db_size = cur.fetchone()[0]
            
            return {
                "status": "healthy",
                "table_count": table_count,
                "database_size": db_size
            }
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}
```

### Best Practices and Common Pitfalls

**Always use parameterized queries to prevent SQL injection**:
```python
# WRONG - vulnerable to SQL injection
user_id = "1; DROP TABLE users; --"
cur.execute(f"SELECT * FROM users WHERE id = {user_id}")

# RIGHT - using parameterized queries
cur.execute("SELECT * FROM users WHERE id = %s", (user_id,))
```

**Proper resource management with context managers**:
```python
# Good practice: automatic cleanup
def safe_database_operation():
    with psycopg.connect(conn_string) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM users")
            return cur.fetchall()
    # Connection and cursor automatically closed
```

**Handle database errors appropriately**:
```python
import psycopg.errors

def robust_database_operation():
    try:
        with psycopg.connect(conn_string) as conn:
            with conn.cursor() as cur:
                cur.execute("INSERT INTO users (email) VALUES (%s)", ("user@example.com",))
                conn.commit()
    except psycopg.errors.UniqueViolation:
        print("User already exists")
    except psycopg.errors.ConnectionError:
        print("Database connection failed")
    except psycopg.errors.Error as e:
        print(f"Database error: {e}")
```

---

## Multiprocessing Library

The multiprocessing library enables parallel execution using multiple processes, which is crucial for CPU-intensive data processing tasks. Unlike threading, multiprocessing can utilize multiple CPU cores effectively and avoids Python's Global Interpreter Lock (GIL).

### Core Concepts and Basic Usage

**Creating and managing processes**
```python
import multiprocessing as mp
import time
import os

def worker_function(name, duration):
    """Simple worker function that simulates work"""
    print(f"Worker {name} starting (PID: {os.getpid()})")
    time.sleep(duration)
    print(f"Worker {name} completed after {duration} seconds")
    return f"Result from {name}"

# Creating and starting processes
def basic_multiprocessing():
    # Create processes
    process1 = mp.Process(target=worker_function, args=("A", 2))
    process2 = mp.Process(target=worker_function, args=("B", 3))
    
    # Start processes
    process1.start()
    process2.start()
    
    # Wait for completion
    process1.join()
    process2.join()
    
    print("All processes completed")

if __name__ == "__main__":
    basic_multiprocessing()
```

**Using Process Pools for better management**
```python
def process_data_chunk(chunk):
    """Process a chunk of data - CPU intensive task"""
    result = []
    for item in chunk:
        # Simulate complex calculation
        processed = sum(i**2 for i in range(item))
        result.append(processed)
    return result

def parallel_data_processing():
    # Data to process
    data = list(range(100, 200))
    chunk_size = 10
    
    # Split data into chunks
    chunks = [data[i:i + chunk_size] for i in range(0, len(data), chunk_size)]
    
    # Use Pool for parallel processing
    with mp.Pool(processes=4) as pool:
        results = pool.map(process_data_chunk, chunks)
    
    # Flatten results
    final_result = [item for sublist in results for item in sublist]
    return final_result

if __name__ == "__main__":
    results = parallel_data_processing()
    print(f"Processed {len(results)} items")
```

### Inter-Process Communication

**Using Queues for communication between processes**
```python
import multiprocessing as mp
import queue
import random
import time

def producer(q, producer_id, num_items):
    """Produces items and puts them in the queue"""
    for i in range(num_items):
        item = f"Item-{producer_id}-{i}"
        q.put(item)
        print(f"Producer {producer_id} produced: {item}")
        time.sleep(random.uniform(0.1, 0.5))
    
    # Signal completion
    q.put(None)

def consumer(q, consumer_id):
    """Consumes items from the queue"""
    processed_items = []
    while True:
        try:
            item = q.get(timeout=2)
            if item is None:
                # Received termination signal
                break
            
            # Process the item
            processed_items.append(f"Processed by {consumer_id}: {item}")
            print(f"Consumer {consumer_id} processed: {item}")
            time.sleep(random.uniform(0.1, 0.3))
            
        except queue.Empty:
            print(f"Consumer {consumer_id} timed out waiting for items")
            break
    
    return processed_items

def producer_consumer_example():
    # Create a queue
    q = mp.Queue(maxsize=5)  # Limited size queue
    
    # Create processes
    producer_proc = mp.Process(target=producer, args=(q, "P1", 10))
    consumer_proc = mp.Process(target=consumer, args=(q, "C1"))
    
    # Start processes
    producer_proc.start()
    consumer_proc.start()
    
    # Wait for completion
    producer_proc.join()
    consumer_proc.join()

if __name__ == "__main__":
    producer_consumer_example()
```

**Shared memory for large data structures**
```python
import multiprocessing as mp
import numpy as np
from multiprocessing import shared_memory

def process_shared_array(shared_name, shape, dtype, start_idx, end_idx):
    """Process a portion of shared array"""
    # Attach to existing shared memory
    existing_shm = shared_memory.SharedMemory(name=shared_name)
    array = np.ndarray(shape, dtype=dtype, buffer=existing_shm.buf)
    
    # Process assigned portion
    for i in range(start_idx, end_idx):
        array[i] = array[i] ** 2  # Square the values
    
    # Don't close here - parent will handle cleanup
    print(f"Processed indices {start_idx} to {end_idx}")

def shared_memory_example():
    # Create large array
    size = 1000000
    data = np.random.randint(1, 100, size=size)
    
    # Create shared memory
    shm = shared_memory.SharedMemory(create=True, size=data.nbytes)
    shared_array = np.ndarray(data.shape, dtype=data.dtype, buffer=shm.buf)
    shared_array[:] = data[:]  # Copy data
    
    # Process in parallel chunks
    num_processes = 4
    chunk_size = size // num_processes
    processes = []
    
    for i in range(num_processes):
        start_idx = i * chunk_size
        end_idx = start_idx + chunk_size if i < num_processes - 1 else size
        
        p = mp.Process(
            target=process_shared_array,
            args=(shm.name, shared_array.shape, shared_array.dtype, start_idx, end_idx)
        )
        processes.append(p)
        p.start()
    
    # Wait for all processes to complete
    for p in processes:
        p.join()
    
    print(f"First 10 processed values: {shared_array[:10]}")
    
    # Cleanup
    shm.close()
    shm.unlink()

if __name__ == "__main__":
    shared_memory_example()
```

### Advanced Patterns and Use Cases

**Data pipeline with multiple stages**
```python
def data_pipeline_multiprocessing():
    """Complex data processing pipeline using multiple processes"""
    
    def extract_data(output_queue):
        """Simulate data extraction"""
        for i in range(100):
            raw_data = f"raw_data_{i}"
            output_queue.put(raw_data)
            time.sleep(0.01)
        output_queue.put(None)  # Signal completion
    
    def transform_data(input_queue, output_queue):
        """Transform raw data"""
        while True:
            try:
                data = input_queue.get(timeout=5)
                if data is None:
                    break
                
                # Simulate transformation
                transformed = f"transformed_{data}"
                output_queue.put(transformed)
                
            except queue.Empty:
                break
        
        output_queue.put(None)  # Signal completion
    
    def load_data(input_queue, results_list):
        """Load transformed data"""
        while True:
            try:
                data = input_queue.get(timeout=5)
                if data is None:
                    break
                
                # Simulate loading to database/file
                results_list.append(f"loaded_{data}")
                
            except queue.Empty:
                break
    
    # Create queues for communication
    extract_to_transform = mp.Queue(maxsize=10)
    transform_to_load = mp.Queue(maxsize=10)
    
    # Shared list for results
    manager = mp.Manager()
    results = manager.list()
    
    # Create processes
    extractor = mp.Process(target=extract_data, args=(extract_to_transform,))
    transformer = mp.Process(target=transform_data, args=(extract_to_transform, transform_to_load))
    loader = mp.Process(target=load_data, args=(transform_to_load, results))
    
    # Start all processes
    extractor.start()
    transformer.start()
    loader.start()
    
    # Wait for completion
    extractor.join()
    transformer.join()
    loader.join()
    
    print(f"Pipeline processed {len(results)} items")
    return list(results)

if __name__ == "__main__":
    results = data_pipeline_multiprocessing()
```

**Error handling and process monitoring**
```python
def monitored_worker(worker_id, work_queue, result_queue, error_queue):
    """Worker with comprehensive error handling"""
    try:
        while True:
            try:
                task = work_queue.get(timeout=2)
                if task is None:
                    break
                
                # Simulate work that might fail
                if task % 7 == 0:  # Simulate random errors
                    raise ValueError(f"Task {task} failed randomly")
                
                result = task ** 2
                result_queue.put((worker_id, task, result))
                
            except queue.Empty:
                break
            except Exception as e:
                error_info = {
                    'worker_id': worker_id,
                    'task': task,
                    'error': str(e),
                    'timestamp': time.time()
                }
                error_queue.put(error_info)
                
    except Exception as e:
        # Critical error in worker
        error_queue.put({
            'worker_id': worker_id,
            'critical_error': str(e),
            'timestamp': time.time()
        })

def robust_multiprocessing():
    # Create queues
    work_queue = mp.Queue()
    result_queue = mp.Queue()
    error_queue = mp.Queue()
    
    # Add tasks
    tasks = list(range(100))
    for task in tasks:
        work_queue.put(task)
    
    # Add termination signals
    num_workers = 4
    for _ in range(num_workers):
        work_queue.put(None)
    
    # Start workers
    workers = []
    for i in range(num_workers):
        worker = mp.Process(
            target=monitored_worker,
            args=(i, work_queue, result_queue, error_queue)
        )
        worker.start()
        workers.append(worker)
    
    # Monitor progress
    completed_tasks = 0
    errors = []
    results = []
    
    while completed_tasks < len(tasks) or any(w.is_alive() for w in workers):
        # Check for results
        try:
            worker_id, task, result = result_queue.get(timeout=0.1)
            results.append((task, result))
            completed_tasks += 1
        except queue.Empty:
            pass
        
        # Check for errors
        try:
            error = error_queue.get(timeout=0.1)
            errors.append(error)
            if 'task' in error:
                completed_tasks += 1  # Count failed tasks as completed
        except queue.Empty:
            pass
    
    # Wait for all workers to finish
    for worker in workers:
        worker.join()
    
    print(f", r'\1-\2-\3', regex=True))
        
        # Clean names
        df_clean['name'] = (df_clean['name']
                           .str.strip()
                           .str.title()
                           .replace('', np.nan))
        
        return df_clean
    
    # Remove duplicates
    def handle_duplicates(df):
        # Check for duplicates
        print(f"Duplicate rows: {df.duplicated().sum()}")
        
        # Remove exact duplicates
        df_no_dupes = df.drop_duplicates()
        
        # Remove duplicates based on specific columns
        df_no_dupes_subset = df.drop_duplicates(subset=['name', 'email'])
        
        # Keep last occurrence instead of first
        df_keep_last = df.drop_duplicates(keep='last')
        
        return df_no_dupes
    
    # Apply all cleaning steps
    df_cleaned = handle_missing_values(df)
    df_cleaned = convert_data_types(df_cleaned)
    df_cleaned = clean_string_data(df_cleaned)
    df_cleaned = handle_duplicates(df_cleaned)
    
    print("\nCleaned data:")
    print(df_cleaned)
    print(f"Shape after cleaning: {df_cleaned.shape}")
    
    return df_cleaned
```

### Advanced Data Manipulation

**Grouping, aggregation, and transformation operations**
```python
def advanced_groupby_operations():
    """Comprehensive groupby operations"""
    
    # Create sample sales data
    np.random.seed(42)
    dates = pd.date_range('2023-01-01', periods=1000, freq='D')
    data = {
        'date': np.random.choice(dates, 5000),
        'product': np.random.choice(['A', 'B', 'C', 'D'], 5000),
        'region': np.random.choice(['North', 'South', 'East', 'West'], 5000),
        'sales': np.random.uniform(100, 1000, 5000),
        'quantity': np.random.randint(1, 50, 5000),
        'salesperson': np.random.choice(['Alice', 'Bob', 'Charlie', 'Diana'], 5000)
    }
    df = pd.DataFrame(data)
    
    # Basic groupby operations
    def basic_groupby(df):
        # Single column grouping
        product_sales = df.groupby('product')['sales'].sum()
        print("Sales by product:")
        print(product_sales)
        
        # Multiple column grouping
        region_product_sales = df.groupby(['region', 'product'])['sales'].sum()
        print("\nSales by region and product:")
        print(region_product_sales)
        
        # Multiple aggregations
        summary = df.groupby('product').agg({
            'sales': ['sum', 'mean', 'count'],
            'quantity': ['sum', 'mean'],
            'salesperson': 'nunique'
        })
        print("\nMultiple aggregations:")
        print(summary)
    
    # Advanced aggregations
    def advanced_aggregations(df):
        # Custom aggregation functions
        def range_calc(x):
            return x.max() - x.min()
        
        custom_agg = df.groupby('product').agg({
            'sales': ['sum', 'mean', range_calc],
            'quantity': ['sum', lambda x: x.quantile(0.75)]
        })
        
        # Named aggregations (pandas 0.25+)
        named_agg = df.groupby('product').agg(
            total_sales=('sales', 'sum'),
            avg_sales=('sales', 'mean'),
            max_quantity=('quantity', 'max'),
            unique_salespeople=('salesperson', 'nunique')
        )
        print("Named aggregations:")
        print(named_agg)
        
        # Conditional aggregation
        high_value_sales = df[df['sales'] > 500].groupby('product')['sales'].sum()
        print("\nHigh value sales by product:")
        print(high_value_sales)
    
    # Transform operations
    def transform_operations(df):
        # Add group statistics as new columns
        df['product_mean_sales'] = df.groupby('product')['sales'].transform('mean')
        df['region_total_sales'] = df.groupby('region')['sales'].transform('sum')
        df['sales_rank_in_product'] = df.groupby('product')['sales'].rank(method='dense', ascending=False)
        
        # Normalize within groups
        df['sales_normalized'] = df.groupby('product')['sales'].transform(lambda x: (x - x.mean()) / x.std())
        
        # Calculate rolling statistics within groups
        df_sorted = df.sort_values(['product', 'date'])
        df_sorted['rolling_avg_sales'] = (df_sorted.groupby('product')['sales']
                                         .transform(lambda x: x.rolling(window=7, min_periods=1).mean()))
        
        return df_sorted
    
    # Apply all operations
    basic_groupby(df)
    advanced_aggregations(df)
    df_transformed = transform_operations(df)
    
    return df_transformed

def merging_and_joining_operations():
    """Comprehensive merge and join operations"""
    
    # Create sample datasets
    employees = pd.DataFrame({
        'emp_id': [1, 2, 3, 4, 5],
        'name': ['Alice', 'Bob', 'Charlie', 'Diana', 'Eve'],
        'department': ['HR', 'IT', 'Finance', 'IT', 'HR'],
        'salary': [70000, 80000, 75000, 85000, 72000]
    })
    
    departments = pd.DataFrame({
        'dept_name': ['HR', 'IT', 'Finance', 'Marketing'],
        'manager': ['John', 'Jane', 'Mike', 'Sarah'],
        'budget': [500000, 1000000, 800000, 600000]
    })
    
    projects = pd.DataFrame({
        'project_id': [101, 102, 103, 104],
        'emp_id': [1, 2, 2, 3],
        'project_name': ['Project A', 'Project B', 'Project C', 'Project D'],
        'hours': [40, 30, 20, 35]
    })
    
    # Different types of merges
    def merge_operations():
        # Inner join (default)
        inner_merge = pd.merge(employees, departments, 
                              left_on='department', right_on='dept_name')
        print("Inner merge:")
        print(inner_merge)
        
        # Left join
        left_merge = pd.merge(employees, departments, 
                             left_on='department', right_on='dept_name', how='left')
        print("\nLeft merge:")
        print(left_merge)
        
        # Right join
        right_merge = pd.merge(employees, departments, 
                              left_on='department', right_on='dept_name', how='right')
        print("\nRight merge:")
        print(right_merge)
        
        # Outer join
        outer_merge = pd.merge(employees, departments, 
                              left_on='department', right_on='dept_name', how='outer')
        print("\nOuter merge:")
        print(outer_merge)
    
    # Multiple joins
    def complex_joins():
        # First merge employees with projects
        emp_projects = pd.merge(employees, projects, on='emp_id', how='left')
        
        # Then merge with departments
        full_data = pd.merge(emp_projects, departments, 
                            left_on='department', right_on='dept_name', how='left')
        
        print("Multiple joins result:")
        print(full_data)
        
        # Alternative: chain merges
        result = (employees
                 .merge(projects, on='emp_id', how='left')
                 .merge(departments, left_on='department', right_on='dept_name', how='left'))
        
        return result
    
    # Concatenation operations
    def concatenation_operations():
        # Create additional employee data
        new_employees = pd.DataFrame({
            'emp_id': [6, 7, 8],
            'name': ['Frank', 'Grace', 'Henry'],
            'department': ['IT', 'Finance', 'Marketing'],
            'salary': [78000, 73000, 71000]
        })
        
        # Vertical concatenation (append rows)
        all_employees = pd.concat([employees, new_employees], ignore_index=True)
        print("Concatenated employees:")
        print(all_employees)
        
        # Horizontal concatenation (append columns)
        employee_details = pd.DataFrame({
            'emp_id': [1, 2, 3, 4, 5],
            'age': [28, 32, 29, 31, 27],
            'location': ['NY', 'CA', 'TX', 'FL', 'WA']
        })
        
        horizontal_concat = pd.concat([employees.set_index('emp_id'), 
                                      employee_details.set_index('emp_id')], axis=1)
        print("\nHorizontal concatenation:")
        print(horizontal_concat)
    
    merge_operations()
    complex_joins()
    concatenation_operations()
    
    return "Merge operations completed"

def time_series_operations():
    """Advanced time series data manipulation"""
    
    # Create time series data
    dates = pd.date_range('2023-01-01', periods=365, freq='D')
    ts_data = pd.DataFrame({
        'date': dates,
        'sales': np.random.uniform(100, 1000, 365) + 
                np.sin(np.arange(365) * 2 * np.pi / 365) * 100,  # Seasonal pattern
        'temperature': np.random.normal(20, 10, 365),
        'region': np.random.choice(['North', 'South'], 365)
    })
    
    # Set date as index
    ts_data.set_index('date', inplace=True)
    
    def datetime_operations():
        # Extract date components
        ts_data['year'] = ts_data.index.year
        ts_data['month'] = ts_data.index.month
        ts_data['day'] = ts_data.index.day
        ts_data['day_of_week'] = ts_data.index.day_of_week
        ts_data['quarter'] = ts_data.index.quarter
        
        # Create period index
        ts_data['month_period'] = ts_data.index.to_period('M')
        
        # Date arithmetic
        ts_data['days_from_start'] = (ts_data.index - ts_data.index[0]).days
        
        print("Date operations:")
        print(ts_data.head())
    
    def resampling_operations():
        # Resample to different frequencies
        
        # Monthly aggregation
        monthly_sales = ts_data['sales'].resample('M').agg({
            'total': 'sum',
            'average': 'mean',
            'max': 'max',
            'min': 'min'
        })
        print("Monthly sales summary:")
        print(monthly_sales.head())
        
        # Weekly aggregation
        weekly_avg = ts_data.resample('W').mean()
        
        # Custom aggregation
        quarterly_summary = ts_data.resample('Q').agg({
            'sales': ['sum', 'mean', 'std'],
            'temperature': ['mean', 'min', 'max']
        })
        
        # Upsampling (increase frequency)
        daily_to_hourly = ts_data.resample('H').interpolate()
        
        return monthly_sales, weekly_avg, quarterly_summary
    
    def rolling_operations():
        # Rolling window calculations
        ts_data['sales_7day_ma'] = ts_data['sales'].rolling(window=7).mean()
        ts_data['sales_30day_ma'] = ts_data['sales'].rolling(window=30).mean()
        
        # Rolling with different functions
        ts_data['sales_7day_std'] = ts_data['sales'].rolling(window=7).std()
        ts_data['sales_7day_max'] = ts_data['sales'].rolling(window=7).max()
        
        # Expanding window (cumulative)
        ts_data['cumulative_sales'] = ts_data['sales'].expanding().sum()
        ts_data['cumulative_avg'] = ts_data['sales'].expanding().mean()
        
        # Rolling with custom function
        def coefficient_of_variation(x):
            return x.std() / x.mean() if x.mean() != 0 else 0
        
        ts_data['sales_cv'] = ts_data['sales'].rolling(window=30).apply(coefficient_of_variation)
        
        print("Rolling operations:")
        print(ts_data[['sales', 'sales_7day_ma', 'sales_30day_ma']].head(40))
    
    def shift_and_lag_operations():
        # Lag operations
        ts_data['sales_lag1'] = ts_data['sales'].shift(1)
        ts_data['sales_lag7'] = ts_data['sales'].shift(7)
        
        # Lead operations
        ts_data['sales_lead1'] = ts_data['sales'].shift(-1)
        
        # Percentage change
        ts_data['sales_pct_change'] = ts_data['sales'].pct_change()
        ts_data['sales_pct_change_7d'] = ts_data['sales'].pct_change(periods=7)
        
        # Difference operations
        ts_data['sales_diff'] = ts_data['sales'].diff()
        ts_data['sales_diff_7d'] = ts_data['sales'].diff(periods=7)
        
        print("Shift and lag operations:")
        print(ts_data[['sales', 'sales_lag1', 'sales_pct_change']].head(10))
    
    datetime_operations()
    resampling_operations()
    rolling_operations()
    shift_and_lag_operations()
    
    return ts_data
```

### Performance Optimization and Memory Management

**Efficient data processing techniques**
```python
def performance_optimization():
    """Techniques for optimizing pandas performance"""
    
    # Memory-efficient data types
    def optimize_datatypes():
        # Create sample data
        df = pd.DataFrame({
            'id': range(1000000),
            'category': np.random.choice(['A', 'B', 'C'], 1000000),
            'value': np.random.uniform(0, 100, 1000000),
            'flag': np.random.choice([True, False], 1000000)
        })
        
        print("Original memory usage:")
        print(df.memory_usage(deep=True))
        print(f"Total memory: {df.memory_usage(deep=True).sum() / 1024**2:.2f} MB")
        
        # Optimize integer columns
        df['id'] = df['id'].astype('int32')  # Instead of int64
        
        # Use category for string columns with few unique values
        df['category'] = df['category'].astype('category')
        
        # Use float32 instead of float64 when precision allows
        df['value'] = df['value'].astype('float32')
        
        print("\nOptimized memory usage:")
        print(df.memory_usage(deep=True))
        print(f"Total memory: {df.memory_usage(deep=True).sum() / 1024**2:.2f} MB")
        
        return df
    
    def chunked_processing():
        """Process large files in chunks"""
        
        def process_large_csv(filename, chunk_size=10000):
            results = []
            
            # Process file in chunks
            for chunk in pd.read_csv(filename, chunksize=chunk_size):
                # Process each chunk
                processed_chunk = chunk.groupby('category')['value'].sum()
                results.append(processed_chunk)
            
            # Combine results
            final_result = pd.concat(results).groupby(level=0).sum()
            return final_result
        
        # Alternative: use iterator
        def process_with_iterator(filename):
            chunk_iter = pd.read_csv(filename, chunksize=10000)
            total_sum = 0
            
            for chunk in chunk_iter:
                total_sum += chunk['value'].sum()
            
            return total_sum
    
    def vectorized_operations():
        """Use vectorized operations instead of loops"""
        
        df = pd.DataFrame({
            'A': np.random.randint(1, 100, 100000),
            'B': np.random.randint(1, 100, 100000),
            'C': np.random.uniform(0, 1, 100000)
        })
        
        # SLOW: Using iterrows
        def slow_calculation(df):
            result = []
            for index, row in df.iterrows():
                if row['A'] > 50:
                    result.append(row['B'] * row['C'])
                else:
                    result.append(0)
            return result
        
        # FAST: Using vectorized operations
        def fast_calculation(df):
            return np.where(df['A'] > 50, df['B'] * df['C'], 0)
        
        # FASTEST: Using pandas operations
        def fastest_calculation(df):
            return (df['B'] * df['C']).where(df['A'] > 50, 0)
        
        # Timing comparison
        import time
        
        start = time.time()
        result_fast = fast_calculation(df)
        fast_time = time.time() - start
        
        print(f"Vectorized operation time: {fast_time:.4f} seconds")
        
        return result_fast
    
    def efficient_string_operations():
        """Optimize string operations"""
        
        df = pd.DataFrame({
            'text': ['Hello World', 'pandas optimization', 'string operations'] * 10000
        })
        
        # Use string accessor for vectorized string operations
        df['text_upper'] = df['text'].str.upper()
        df['text_length'] = df['text'].str.len()
        df['contains_pandas'] = df['text'].str.contains('pandas')
        
        # Use regex for complex patterns
        df['extract_first_word'] = df['text'].str.extract(r'(\w+)')
        
        # Use categorical for repetitive strings
        df['text_category'] = df['text'].astype('category')
        
        return df
    
    def query_optimization():
        """Optimize filtering and querying"""
        
        df = pd.DataFrame({
            'A': np.random.randint(1, 1000, 100000),
            'B': np.random.uniform(0, 100, 100000),
            'C': np.random.choice(['X', 'Y', 'Z'], 100000)
        })
        
        # Use query() for complex conditions (can be faster)
        result1 = df.query('A > 500 and B < 50 and C == "X"')
        
        # Use index for frequent lookups
        df_indexed = df.set_index('A')
        specific_rows = df_indexed.loc[500:600]
        
        # Use categorical index for string lookups
        df['C'] = df['C'].astype('category')
        df_cat_indexed = df.set_index('C')
        
        return result1
    
    # Run optimizations
    optimized_df = optimize_datatypes()
    vectorized_result = vectorized_operations()
    string_optimized = efficient_string_operations()
    
    return optimized_df

def advanced_data_validation():
    """Data validation and quality checks"""
    
    def create_validation_framework():
        """Create a comprehensive data validation framework"""
        
        class DataValidator:
            def __init__(self, df):
                self.df = df
                self.validation_results = {}
            
            def check_null_values(self, columns=None, max_null_pct=0.05):
                """Check for null values in specified columns"""
                columns = columns or self.df.columns
                results = {}
                
                for col in columns:
                    null_count = self.df[col].isnull().sum()
                    null_pct = null_count / len(self.df)
                    results[col] = {
                        'null_count': null_count,
                        'null_percentage': null_pct,
                        'passes': null_pct <= max_null_pct
                    }
                
                self.validation_results['null_check'] = results
                return results
            
            def check_data_types(self, expected_types):
                """Validate data types"""
                results = {}
                
                for col, expected_type in expected_types.items():
                    if col in self.df.columns:
                        actual_type = self.df[col].dtype
                        results[col] = {
                            'expected': expected_type,
                            'actual': str(actual_type),
                            'passes': str(actual_type) == expected_type
                        }
                
                self.validation_results['type_check'] = results
                return results
            
            def check_value_ranges(self, range_checks):
                """Check if values are within expected ranges"""
                results = {}
                
                for col, (min_val, max_val) in range_checks.items():
                    if col in self.df.columns:
                        out_of_range = ((self.df[col] < min_val) | 
                                       (self.df[col] > max_val)).sum()
                        results[col] = {
                            'min_expected': min_val,
                            'max_expected': max_val,
                            'min_actual': self.df[col].min(),
                            'max_actual': self.df[col].max(),
                            'out_of_range_count': out_of_range,
                            'passes': out_of_range == 0
                        }
                
                self.validation_results['range_check'] = results
                return results
            
            def check_unique_constraints(self, unique_columns):
                """Check uniqueness constraints"""
                results = {}
                
                for col in unique_columns:
                    if col in self.df.columns:
                        duplicate_count = self.df[col].duplicated().sum()
                        results[col] = {
                            'duplicate_count': duplicate_count,
                            'passes': duplicate_count == 0
                        }
                
                self.validation_results['unique_check'] = results
                return results
            
            def check_referential_integrity(self, foreign_keys):
                """Check foreign key constraints"""
                results = {}
                
                for local_col, (ref_df, ref_col) in foreign_keys.items():
                    if local_col in self.df.columns:
                        missing_refs = ~self.df[local_col].isin(ref_df[ref_col])
                        missing_count = missing_refs.sum()
                        results[local_col] = {
                            'missing_references': missing_count,
                            'passes': missing_count == 0
                        }
                
                self.validation_results['referential_check'] = results
                return results
            
            def generate_report(self):
                """Generate comprehensive validation report"""
                report = {
                    'total_records': len(self.df),
                    'total_columns': len(self.df.columns),
                    'validation_summary': {},
                    'details': self.validation_results
                }
                
                # Summarize results
                for check_type, results in self.validation_results.items():
                    if isinstance(results, dict):
                        passed = sum(1 for r in results.values() if r.get('passes', False))
                        total = len(results)
                        report['validation_summary'][check_type] = {
                            'passed': passed,
                            'total': total,
                            'pass_rate': passed / total if total > 0 else 0
                        }
                
                return report
        
        return DataValidator
    
    # Example usage
    def run_validation_example():
        # Create sample data with issues
        data = {
            'id': [1, 2, 3, 4, 5, 5],  # Duplicate ID
            'name': ['Alice', 'Bob', '', 'Diana', 'Eve', 'Frank'],
            'age': [25, 30, 150, 28, 35, 22],  # Invalid age
            'salary': [70000, 80000, 90000, None, 85000, 60000],  # Missing salary
            'department_id': [1, 2, 3, 4, 2, 1]
        }
        df = pd.DataFrame(data)
        
        # Reference data for foreign key check
        departments = pd.DataFrame({
            'dept_id': [1, 2, 3],
            'dept_name': ['HR', 'IT', 'Finance']
        })
        
        # Create validator
        DataValidator = create_validation_framework()
        validator = DataValidator(df)
        
        # Run validations
        validator.check_null_values(max_null_pct=0.1)
        validator.check_data_types({
            'id': 'int64',
            'name': 'object',
            'age': 'int64'
        })
        validator.check_value_ranges({
            'age': (18, 100),
            'salary': (30000, 200000)
        })
        validator.check_unique_constraints(['id'])
        validator.check_referential_integrity({
            'department_id': (departments, 'dept_id')
        })
        
        # Generate report
        report = validator.generate_report()
        print("Validation Report:")
        print(json.dumps(report, indent=2, default=str))
        
        return report
    
    return run_validation_example()
```

### Best Practices and Common Pitfalls

**Essential pandas best practices**
```python
def pandas_best_practices():
    """Essential best practices for pandas usage"""
    
    def memory_management():
        """Best practices for memory management"""
        
        # 1. Use appropriate data types
        df = pd.DataFrame({
            'category': ['A', 'B', 'C'] * 1000,  # Use category type
            'small_int': range(3000),  # Use int32 instead of int64
            'flag': [True, False] * 1500  # bool is memory efficient
        })
        
        # Convert to more efficient types
        df['category'] = df['category'].astype('category')
        df['small_int'] = df['small_int'].astype('int32')
        
        # 2. Drop unnecessary columns early
        df = df.drop(['unnecessary_column'], axis=1, errors='ignore')
        
        # 3. Use del to free memory
        large_temp_df = pd.DataFrame(np.random.rand(100000, 100))
        result = large_temp_df.sum()
        del large_temp_df  # Free memory immediately
        
        # 4. Use copy() wisely
        # Avoid unnecessary copies
        df_view = df[df['small_int'] > 1000]  # This is a view, not a copy
        df_copy = df[df['small_int'] > 1000].copy()  # Explicit copy when needed
        
        return df
    
    def efficient_operations():
        """Best practices for efficient operations"""
        
        df = pd.DataFrame({
            'A': np.random.randint(1, 100, 10000),
            'B': np.random.uniform(0, 1, 10000),
            'text': ['sample text'] * 10000
        })
        
        # 1. Use vectorized operations
        # GOOD
        df['A_squared'] = df['A'] ** 2
        df['A_plus_B'] = df['A'] + df['B']
        
        # 2. Use boolean indexing efficiently
        # GOOD - single condition
        filtered = df[df['A'] > 50]
        
        # GOOD - multiple conditions with parentheses
        complex_filter = df[(df['A'] > 50) & (df['B'] < 0.5)]
        
        # 3. Chain operations efficiently
        result = (df
                 .query('A > 50')
                 .groupby('text')['B']
                 .mean()
                 .reset_index())
        
        # 4. Use .loc and .iloc appropriately
        # GOOD - explicit indexing
        specific_value = df.loc[0, 'A']
        subset = df.iloc[0:100, 0:2]
        
        return result
    
    def common_pitfalls():
        """Common pitfalls to avoid"""
        
        df = pd.DataFrame({
            'A': [1, 2, 3, 4, 5],
            'B': [10, 20, 30, 40, 50]
        })
        
        # PITFALL 1: SettingWithCopyWarning
        # BAD
        try:
            subset = df[df['A'] > 2]
            subset['C'] = subset['B'] * 2  # May trigger warning
        except:
            pass
        
        # GOOD
        subset = df[df['A'] > 2].copy()
        subset['C'] = subset['B'] * 2
        
        # PITFALL 2: Inefficient string operations
        df['text'] = ['hello', 'world', 'pandas', 'data', 'science']
        
        # BAD - using apply with lambda for simple operations
        # df['text_upper'] = df['text'].apply(lambda x: x.upper())
        
        # GOOD - using vectorized string methods
        df['text_upper'] = df['text'].str.upper()
        
        # PITFALL 3: Not handling missing values appropriately
        df_with_na = pd.DataFrame({
            'values': [1, 2, np.nan, 4, 5]
        })
        
        # BAD - ignoring NaN in calculations
        # mean_value = df_with_na['values'].sum() / len(df_with_na)
        
        # GOOD - explicit handling
        mean_value = df_with_na['values'].mean()  # Automatically handles NaN
        
        # PITFALL 4: Not resetting index after operations
        grouped = df.groupby('A').sum()
        # GOOD - reset index if you need A as a column
        grouped_reset = grouped.reset_index()
        
        return df, grouped_reset
    
    def testing_and_debugging():
        """Best practices for testing pandas code"""
        
        def test_data_processing_function():
            """Example of testing a data processing function"""
            
            def process_sales_data(df):
                """Function to test"""
                # Add calculated columns
                df = df.copy()
                df['revenue'] = df['price'] * df['quantity']
                df['revenue_category'] = pd.cut(df['revenue'], 
                                               bins=[0, 1000, 5000, float('inf')], 
                                               labels=['Low', 'Medium', 'High'])
                return df
            
            # Create test data
            test_df = pd.DataFrame({
                'price': [10, 50, 100],
                'quantity': [5, 20, 30]
            })
            
            # Test the function
            result = process_sales_data(test_df)
            
            # Assertions
            assert 'revenue' in result.columns
            assert 'revenue_category' in result.columns
            assert result['revenue'].iloc[0] == 50  # 10 * 5
            assert result['revenue_category'].iloc[0] == 'Low'
            assert len(result) == len(test_df)
            
            print("All tests passed!")
            return result
        
        return test_data_processing_function()
    
    # Run all best practices examples
    memory_management()
    efficient_operations()
    common_pitfalls()
    testing_and_debugging()
    
    return "Best practices demonstration completed"
```

---

## Asyncio Library

Asyncio provides infrastructure for writing concurrent code using the async/await syntax. It's essential for I/O-bound operations in data engineering, such as making multiple API calls, database operations, or file processing concurrently.

### Basic Async/Await Concepts

**Understanding coroutines and event loops**
```python
import asyncio
import aiohttp
import aiofiles
import time
from typing import List, Dict, Any

async def basic_coroutine():
    """Basic coroutine example"""
    print("Coroutine started")
    await asyncio.sleep(1)  # Non-blocking sleep
    print("Coroutine completed")
    return "Hello from coroutine"

async def understanding_async_basics():
    """Demonstrate basic async concepts"""
    
    # Running a single coroutine
    result = await basic_coroutine()
    print(f"Result: {result}")
    
    # Running multiple coroutines concurrently
    tasks = [basic_coroutine() for _ in range(3)]
    results = await asyncio.gather(*tasks)
    print(f"Multiple results: {results}")
    
    # Using asyncio.create_task() for better control
    task1 = asyncio.create_task(basic_coroutine())
    task2 = asyncio.create_task(basic_coroutine())
    
    # Wait for both tasks
    await task1
    await task2
    
    return results

def run_async_function():
    """How to run async functions from synchronous code"""
    # Python 3.7+
    result = asyncio.run(understanding_async_basics())
    return result

# For older Python versions or when you need more control
def run_with_event_loop():
    """Alternative way to run async code"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        result = loop.run_until_complete(understanding_async_basics())
        return result
    finally:
        loop.close()
```

### Concurrent I/O Operations

**Making concurrent HTTP requests and file operations**
```python
async def concurrent_http_requests():
    """Demonstrate concurrent HTTP requests using aiohttp"""
    
    async def fetch_url(session: aiohttp.ClientSession, url: str) -> Dict[str, Any]:
        """Fetch a single URL"""
        try:
            async with session.get(url) as response:
                content = await response.text()
                return {
                    'url': url,
                    'status': response.status,
                    'content_length': len(content),
                    'headers': dict(response.headers)
                }
        except Exception as e:
            return {
                'url': url,
                'error': str(e)
            }
    
    async def fetch_multiple_urls(urls: List[str]) -> List[Dict[str, Any]]:
        """Fetch multiple URLs concurrently"""
        async with aiohttp.ClientSession() as session:
            tasks = [fetch_url(session, url) for url in urls]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            return results
    
    # Example usage
    urls = [
        'https://httpbin.org/delay/1',
        'https://httpbin.org/delay/2',
        'https://httpbin.org/json',
        'https://httpbin.org/headers',
        'https://httpbin.org/user-agent'
    ]
    
    start_time = time.time()
    results = await fetch_multiple_urls(urls)
    end_time = time.time()
    
    print(f"Fetched {len(urls)} URLs in {end_time - start_time:.2f} seconds")
    for result in results:
        if 'error' in result:
            print(f"Error fetching {result['url']}: {result['error']}")
        else:
            print(f"Success: {result['url']} - Status: {result['status']}")
    
    return results

async def concurrent_file_operations():
    """Demonstrate concurrent file operations"""
    
    async def read_file_async(filename: str) -> Dict[str, Any]:
        """Read a file asynchronously"""
        try:
            async with aiofiles.open(filename, 'r') as file:
                content = await file.read()
                return {
                    'filename': filename,
                    'size': len(content),
                    'lines': len(content.splitlines())
                }
        except Exception as e:
            return {
                'filename': filename,
                'error': str(e)
            }
    
    async def write_file_async(filename: str, content: str) -> Dict[str, Any]:
        """Write a file asynchronously"""
        try:
            async with aiofiles.open(filename, 'w') as file:
                await file.write(content)
                return {
                    'filename': filename,
                    'status': 'success',
                    'bytes_written': len(content.encode())
                }
        except Exception as e:
            return {
                'filename': filename,
                'error': str(e)
            }
    
    async def process_files_concurrently(filenames: List[str]) -> List[Dict[str, Any]]:
        """Process multiple files concurrently"""
        # Create some test files first
        test_content = ["File content " + str(i) for i in range(len(filenames))]
        
        # Write files concurrently
        write_tasks = [write_file_async(filename, content) 
                      for filename, content in zip(filenames, test_content)]
        write_results = await asyncio.gather(*write_tasks)
        
        # Read files concurrently
        read_tasks = [read_file_async(filename) for filename in filenames]
        read_results = await asyncio.gather(*read_tasks)
        
        return write_results, read_results
    
    # Example usage
    filenames = [f'test_file_{i}.txt' for i in range(5)]
    write_results, read_results = await process_files_concurrently(filenames)
    
    print("File processing results:")
    for result in read_results:
        if 'error' in result:
            print(f"Error: {result['filename']} - {result['error']}")
        else:
            print(f"Success: {result['filename']} - {result['lines']} lines, {result['size']} bytes")
    
    return read_results

async def concurrent_database_operations():
    """Demonstrate concurrent database operations"""
    
    async def execute_query_async(query: str, params: tuple = None) -> Dict[str, Any]:
        """Execute a database query asynchronously"""
        # This is a mock implementation
        # In real code, you'd use aiopg, asyncpg, or aiomysql
        
        await asyncio.sleep(0.1)  # Simulate database latency
        
        return {
            'query': query,
            'params': params,
            'result': f"Mock result for: {query[:50]}...",
            'execution_time': 0.1
        }
    
    async def bulk_database_operations():
        """Perform multiple database operations concurrently"""
        
        # Different types of queries
        queries = [
            ("SELECT * FROM users WHERE age > %s", (25,)),
            ("SELECT COUNT(*) FROM orders WHERE status = %s", ('completed',)),
            ("SELECT AVG(salary) FROM employees WHERE department = %s", ('IT',)),
            ("SELECT * FROM products WHERE category = %s", ('electronics',)),
            ("SELECT SUM(amount) FROM transactions WHERE date > %s", ('2023-01-01',))
        ]
        
        # Execute all queries concurrently
        tasks = [execute_query_async(query, params) for query, params in queries]
        results = await asyncio.gather(*tasks)
        
        print("Database operations completed:")
        for result in results:
            print(f"Query: {result['query'][:30]}... - Time: {result['execution_time']}s")
        
        return results
    
    return await bulk_database_operations()
```

### Task Management and Control Flow

**Managing tasks, timeouts, and cancellation**
```python
async def task_management_patterns():
    """Demonstrate advanced task management"""
    
    async def long_running_task(task_id: int, duration: float) -> str:
        """Simulate a long-running task"""
        try:
            print(f"Task {task_id} started (duration: {duration}s)")
            await asyncio.sleep(duration)
            print(f"Task {task_id} completed")
            return f"Task {task_id} result"
        except asyncio.CancelledError:
            print(f"Task {task_id} was cancelled")
            raise
    
    async def task_with_timeout():
        """Demonstrate timeout handling"""
        try:
            # Set timeout for the operation
            result = await asyncio.wait_for(
                long_running_task(1, 3.0), 
                timeout=2.0
            )
            return result
        except asyncio.TimeoutError:
            print("Task timed out!")
            return None
    
    async def task_cancellation():
        """Demonstrate task cancellation"""
        # Create a long-running task
        task = asyncio.create_task(long_running_task(2, 5.0))
        
        # Cancel it after 1 second
        await asyncio.sleep(1.0)
        task.cancel()
        
        try:
            await task
        except asyncio.CancelledError:
            print("Task was successfully cancelled")
    
    async def wait_for_first_completion():
        """Wait for the first task to complete"""
        tasks = [
            asyncio.create_task(long_running_task(i, i * 0.5)) 
            for i in range(1, 4)
        ]
        
        # Wait for the first task to complete
        done, pending = await asyncio.wait(
            tasks, 
            return_when=asyncio.FIRST_COMPLETED
        )
        
        # Cancel remaining tasks
        for task in pending:
            task.cancel()
        
        # Get result from completed task
        completed_task = done.pop()
        result = await completed_task
        print(f"First completed: {result}")
        
        return result
    
    async def wait_for_all_with_error_handling():
        """Wait for all tasks with proper error handling"""
        tasks = [
            asyncio.create_task(long_running_task(1, 1.0)),
            asyncio.create_task(long_running_task(2, 2.0)),
            asyncio.create_task(error_prone_task(3))
        ]
        
        # Use gather with return_exceptions=True
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        successful_results = []
        errors = []
        
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                errors.append(f"Task {i+1} failed: {result}")
            else:
                successful_results.append(result)
        
        print(f"Successful: {len(successful_results)}, Errors: {len(errors)}")
        return successful_results, errors
    
    async def error_prone_task(task_id: int) -> str:
        """A task that might fail"""
        await asyncio.sleep(0.5)
        if task_id == 3:
            raise ValueError(f"Task {task_id} failed intentionally")
        return f"Task {task_id} success"
    
    # Run different patterns
    print("=== Timeout Pattern ===")
    await task_with_timeout()
    
    print("\n=== Cancellation Pattern ===")
    await task_cancellation()
    
    print("\n=== First Completion Pattern ===")
    await wait_for_first_completion()
    
    print("\n=== Error Handling Pattern ===")
    await wait_for_all_with_error_handling()

async def producer_consumer_pattern():
    """Implement producer-consumer pattern with asyncio"""
    
    async def producer(queue: asyncio.Queue, producer_id: int, num_items: int):
        """Produce items and put them in the queue"""
        for i in range(num_items):
            item = f"item-{producer_id}-{i}"
            await queue.put(item)
            print(f"Producer {producer_id} produced: {item}")
            await asyncio.sleep(0.1)  # Simulate work
        
        print(f"Producer {producer_id} finished")
    
    async def consumer(queue: asyncio.Queue, consumer_id: int):
        """Consume items from the queue"""
        consumed_items = []
        while True:
            try:
                # Wait for an item with timeout
                item = await asyncio.wait_for(queue.get(), timeout=2.0)
                consumed_items.append(item)
                print(f"Consumer {consumer_id} consumed: {item}")
                queue.task_done()
                await asyncio.sleep(0.05)  # Simulate processing
            except asyncio.TimeoutError:
                print(f"Consumer {consumer_id} timed out, stopping")
                break
        
        return consumed_items
    
    # Create queue
    queue = asyncio.Queue(maxsize=5)
    
    # Create producers and consumers
    producers = [
        asyncio.create_task(producer(queue, i, 5)) 
        for i in range(2)
    ]
    
    consumers = [
        asyncio.create_task(consumer(queue, i)) 
        for i in range(3)
    ]
    
    # Wait for producers to finish
    await asyncio.gather(*producers)
    
    # Wait for queue to be empty
    await queue.join()
    
    # Cancel consumers (they're waiting for more items)
    for consumer_task in consumers:
        consumer_task.cancel()
    
    # Collect results
    results = []
    for consumer_task in consumers:
        try:
            result = await consumer_task
            results.append(result)
        except asyncio.CancelledError:
            pass
    
    print("Producer-consumer pattern completed")
    return results
```

### Real-World Data Engineering Applications

**Practical asyncio applications for data engineering**
```python
class AsyncDataPipeline:
    """Comprehensive async data pipeline example"""
    
    def __init__(self, max_concurrent_requests: int = 10):
        self.semaphore = asyncio.Semaphore(max_concurrent_requests)
        self.session = None
    
    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()
    
    async def fetch_api_data(self, api_url: str, params: Dict = None) -> Dict[str, Any]:
        """Fetch data from API with rate limiting"""
        async with self.semaphore:  # Limit concurrent requests
            try:
                async with self.session.get(api_url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        return {'success': True, 'data': data, 'url': api_url}
                    else:
                        return {'success': False, 'error': f"HTTP {response.status}", 'url': api_url}
            except Exception as e:
                return {'success': False, 'error': str(e), 'url': api_url}
    
    async def process_data_chunk(self, data_chunk: List[Dict]) -> List[Dict]:
        """Process a chunk of data asynchronously"""
        await asyncio.sleep(0.1)  # Simulate processing time
        
        processed = []
        for item in data_chunk:
            if isinstance(item, dict) and 'success' in item and item['success']:
                # Extract and transform data
                processed_item = {
                    'id': item['data'].get('id'),
                    'processed_at': time.time(),
                    'source_url': item['url'],
                    'data_size': len(str(item['data']))
                }
                processed.append(processed_item)
        
        return processed
    
    async def save_to_file(self, data: List[Dict], filename: str) -> bool:
        """Save processed data to file asynchronously"""
        try:
            import json
            async with aiofiles.open(filename, 'w') as f:
                await f.write(json.dumps(data, indent=2))
            return True
        except Exception as e:
            print(f"Error saving to {filename}: {e}")
            return False
    
    async def run_pipeline(self, api_urls: List[str], output_file: str) -> Dict[str, Any]:
        """Run the complete data pipeline"""
        pipeline_start = time.time()
        
        # Step 1: Fetch data from multiple APIs concurrently
        print(f"Fetching data from {len(api_urls)} APIs...")
        fetch_tasks = [self.fetch_api_data(url) for url in api_urls]
        fetch_results = await asyncio.gather(*fetch_tasks)
        
        successful_fetches = [r for r in fetch_results if r['success']]
        failed_fetches = [r for r in fetch_results if not r['success']]
        
        print(f"Successful fetches: {len(successful_fetches)}")
        print(f"Failed fetches: {len(failed_fetches)}")
        
        # Step 2: Process data in chunks
        chunk_size = 10
        chunks = [successful_fetches[i:i + chunk_size] 
                 for i in range(0, len(successful_fetches), chunk_size)]
        
        print(f"Processing {len(chunks)} data chunks...")
        process_tasks = [self.process_data_chunk(chunk) for chunk in chunks]
        processed_chunks = await asyncio.gather(*process_tasks)
        
        # Flatten processed data
        all_processed_data = [item for chunk in processed_chunks for item in chunk]
        
        # Step 3: Save results
        print(f"Saving {len(all_processed_data)} processed records...")
        save_success = await self.save_to_file(all_processed_data, output_file)
        
        pipeline_end = time.time()
        
        return {
            'total_apis': len(api_urls),
            'successful_fetches': len(successful_fetches),
            'failed_fetches': len(failed_fetches),
            'processed_records': len(all_processed_data),
            'save_success': save_success,
            'pipeline_duration': pipeline_end - pipeline_start,
            'failed_urls': [r['url'] for r in failed_fetches]
        }

async def run_data_pipeline_example():
    """Example of running the async data pipeline"""
    
    # Sample API URLs (using httpbin for testing)
    api_urls = [
        'https://httpbin.org/json',
        'https://httpbin.org/headers',
        'https://httpbin.org/user-agent',
        'https://httpbin.org/delay/1',
        'https://httpbin.org/delay/2'
    ]
    
    async with AsyncDataPipeline(max_concurrent_requests=3) as pipeline:
        results = await pipeline.run_pipeline(api_urls, 'pipeline_output.json')
        
        print("\nPipeline Results:")
        for key, value in results.items():
            print(f"{key}: {value}")
        
        return results

async def async_file_processing():
    """Demonstrate async file processing for large datasets"""
    
    async def process_large_file(filename: str, chunk_size: int = 1000) -> Dict[str, Any]:
        """Process a large file in chunks asynchronously"""
        
        async def process_chunk(lines: List[str]) -> Dict[str, int]:
            """Process a chunk of lines"""
            await asyncio.sleep(0.01)  # Simulate processing
            
            word_count = 0
            char_count = 0
            for line in lines:
                words = line.strip().split()
                word_count += len(words)
                char_count += len(line)
            
            return {'words': word_count, 'chars': char_count}
        
        try:
            async with aiofiles.open(filename, 'r') as file:
                chunk_tasks = []
                chunk = []
                
                async for line in file:
                    chunk.append(line)
                    
                    if len(chunk) >= chunk_size:
                        # Process chunk asynchronously
                        task = asyncio.create_task(process_chunk(chunk.copy()))
                        chunk_tasks.append(task)
                        chunk.clear()
                
                # Process remaining lines
                if chunk:
                    task = asyncio.create_task(process_chunk(chunk))
                    chunk_tasks.append(task)
                
                # Wait for all chunks to be processed
                chunk_results = await asyncio.gather(*chunk_tasks)
                
                # Aggregate results
                total_words = sum(result['words'] for result in chunk_results)
                total_chars = sum(result['chars'] for result in chunk_results)
                
                return {
                    'filename': filename,
                    'chunks_processed': len(chunk_results),
                    'total_words': total_words,
                    'total_chars': total_chars
                }
                
        except Exception as e:
            return {'filename': filename, 'error': str(e)}
    
    # Create a test file
    test_filename = 'large_test_file.txt'
    async with aiofiles.open(test_filename, 'w') as f:
        for i in range(10000):
            await f.write(f"This is line {i} with some sample text for processing.\n")
    
    # Process the file
    result = await process_large_file(test_filename)
    print("File processing result:")
    print(result)
    
    return result
```

### Error Handling and Debugging

**Robust error handling in async code**
```python
async def error_handling_patterns():
    """Demonstrate error handling patterns in async code"""
    
    async def unreliable_operation(operation_id: int, failure_rate: float = 0.3) -> str:
        """Simulate an unreliable async operation"""
        import random
        
        await asyncio.sleep(0.1)
        
        if random.random() < failure_rate:
            raise Exception(f"Operation {operation_id} failed randomly")
        
        return f"Operation {operation_id} succeeded"
    
    async def retry_with_exponential_backoff(operation, max_retries: int = 3, base_delay: float = 1.0):
        """Retry an operation with exponential backoff"""
        
        for attempt in range(max_retries):
            try:
                result = await operation()
                return result
            except Exception as e:
                if attempt == max_retries - 1:
                    raise e
                
                delay = base_delay * (2 ** attempt)
                print(f"Attempt {attempt + 1} failed: {e}. Retrying in {delay}s...")
                await asyncio.sleep(delay)
    
    async def circuit_breaker_pattern():
        """Implement a simple circuit breaker pattern"""
        
        class CircuitBreaker:
            def __init__(self, failure_threshold: int = 3, timeout: float = 60.0):
                self.failure_threshold = failure_threshold
                self.timeout = timeout
                self.failure_count = 0
                self.last_failure_time = None
                self.state = 'CLOSED'  # CLOSED, OPEN, HALF_OPEN
            
            async def call(self, operation):
                if self.state == 'OPEN':
                    if time.time() - self.last_failure_time > self.timeout:
                        self.state = 'HALF_OPEN'
                    else:
                        raise Exception("Circuit breaker is OPEN")
                
                try:
                    result = await operation()
                    
                    if self.state == 'HALF_OPEN':
                        self.state = 'CLOSED'
                        self.failure_count = 0
                    
                    return result
                
                except Exception as e:
                    self.failure_count += 1
                    self.last_failure_time = time.time()
                    
                    if self.failure_count >= self.failure_threshold:
                        self.state = 'OPEN'
                    
                    raise e
        
        # Usage example
        breaker = CircuitBreaker()
        
        for i in range(10):
            try:
                result = await breaker.call(lambda: unreliable_operation(i, 0.7))
                print(f"Success: {result}")
            except Exception as e:
                print(f"Failed: {e}")
            
            await asyncio.sleep(0.1)
    
    async def timeout_and_cancellation_handling():
        """Handle timeouts and cancellation gracefully"""
        
        async def cancellable_operation(task_id: int):
            """Operation that handles cancellation gracefully"""
            try:
                for i in range(10):
                    await asyncio.sleep(0.5)
                    print(f"Task {task_id}: Step {i+1}/10")
                
                return f"Task {task_id} completed"
            
            except asyncio.CancelledError:
                print(f"Task {task_id} is cleaning up after cancellation...")
                # Perform cleanup operations
                await asyncio.sleep(0.1)  # Simulate cleanup
                print(f"Task {task_id} cleanup completed")
                raise  # Re-raise the cancellation
        
        # Create multiple tasks
        tasks = [
            asyncio.create_task(cancellable_operation(i))
            for i in range(3)
        ]
        
        try:
            # Wait for tasks with timeout
            results = await asyncio.wait_for(
                asyncio.gather(*tasks),
                timeout=3.0
            )
            return results
        
        except asyncio.TimeoutError:
            print("Operations timed out, cancelling tasks...")
            
            # Cancel all tasks
            for task in tasks:
                task.cancel()
            
            # Wait for cancellation to complete
            await asyncio.gather(*tasks, return_exceptions=True)
            
            print("All tasks cancelled and cleaned up")
    
    # Run error handling examples
    print("=== Retry with Exponential Backoff ===")
    try:
        result = await retry_with_exponential_backoff(lambda: unreliable_operation(1, 0.8))
        print(f"Final result: {result}")
    except Exception as e:
        print(f"Operation failed after retries: {e}")
    
    print("\n=== Circuit Breaker Pattern ===")
    await circuit_breaker_pattern()
    
    print("\n=== Timeout and Cancellation ===")
    await timeout_and_cancellation_handling()

async def async_debugging_techniques():
    """Debugging techniques for async code"""
    
    # Enable asyncio debug mode
    import asyncio
    import logging
    
    # Set up logging for asyncio
    logging.basicConfig(level=logging.DEBUG)
    asyncio_logger = logging.getLogger('asyncio')
    asyncio_logger.setLevel(logging.DEBUG)
    
    async def debug_slow_operation():
        """Operation with debug information"""
        start_time = time.time()
        
        print(f"Starting operation at {start_time}")
        
        # Use asyncio.current_task() to get current task info
        current_task = asyncio.current_task()
        print(f"Current task: {current_task.get_name() if current_task else 'None'}")
        
        await asyncio.sleep(1)
        
        end_time = time.time()
        print(f"Operation completed in {end_time - start_time:.2f} seconds")
        
        return "Debug operation completed"
    
    # Create named tasks for better debugging
    task = asyncio.create_task(debug_slow_operation(), name="debug_operation")
    result = await task
    
    print(f"Debug result: {result}")
    return result
```

### Best Practices and Performance Tips

**Optimizing asyncio performance and avoiding common pitfalls**
```python
def asyncio_best_practices():
    """Best practices for asyncio usage"""
    
    async def correct_async_patterns():
        """Demonstrate correct async patterns"""
        
        # 1. Use asyncio.gather() for concurrent execution
        async def concurrent_operations():
            # GOOD - truly concurrent
            tasks = [asyncio.sleep(1) for _ in range(3)]
            await asyncio.gather(*tasks)  # Takes ~1 second total
            
            # BAD - sequential execution
            # for _ in range(3):
            #     await asyncio.sleep(1)  # Takes ~3 seconds total
        
        # 2. Use session objects for HTTP requests
        async def efficient_http_requests():
            # GOOD - reuse session
            async with aiohttp.ClientSession() as session:
                tasks = [session.get('https://httpbin.org/delay/1') for _ in range(5)]
                responses = await asyncio.gather(*tasks)
                for response in responses:
                    await response.text()
                    response.close()
            
            # BAD - creating new session for each request
            # responses = []
            # for _ in range(5):
            #     async with aiohttp.ClientSession() as session:
            #         response = await session.get('https://httpbin.org/delay/1')
            #         responses.append(response)
        
        # 3. Use asyncio.Queue for producer-consumer patterns
        async def efficient_queue_usage():
            queue = asyncio.Queue(maxsize=100)  # Limit queue size
            
            async def producer():
                for i in range(10):
                    await queue.put(f"item-{i}")
                await queue.put(None)  # Sentinel value
            
            async def consumer():
                items = []
                while True:
                    item = await queue.get()
                    if item is None:
                        break
                    items.append(item)
                    queue.task_done()
                return items
            
            # Run producer and consumer concurrently
            producer_task = asyncio.create_task(producer())
            consumer_task = asyncio.create_task(consumer())
            
            await producer_task
            items = await consumer_task
            
            return items
        
        await concurrent_operations()
        await efficient_http_requests()
        items = await efficient_queue_usage()
        return items
    
    async def avoid_common_pitfalls():
        """Common pitfalls to avoid in asyncio"""
        
        # 1. Don't use blocking operations in async functions
        async def blocking_pitfall():
            # BAD - blocks the event loop
            # time.sleep(1)  # This blocks everything!
            
            # GOOD - use async equivalent
            await asyncio.sleep(1)
        
        # 2. Don't forget to await coroutines
        async def await_pitfall():
            # BAD - creates coroutine but doesn't execute it
            # asyncio.sleep(1)  # This does nothing!
            
            # GOOD - actually wait for the coroutine
            await asyncio.sleep(1)
        
        # 3. Handle exceptions in gather()
        async def exception_handling():
            async def failing_task():
                await asyncio.sleep(0.1)
                raise ValueError("Task failed")
            
            async def succeeding_task():
                await asyncio.sleep(0.2)
                return "Success"
            
            # GOOD - handle exceptions properly
            results = await asyncio.gather(
                failing_task(),
                succeeding_task(),
                return_exceptions=True
            )
            
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    print(f"Task {i} failed: {result}")
                else:
                    print(f"Task {i} succeeded: {result}")
        
        await blocking_pitfall()
        await await_pitfall()
        await exception_handling()
    
    async def performance_optimization():
        """Performance optimization techniques"""
        
        # 1. Use semaphores to limit concurrency
        semaphore = asyncio.Semaphore(5)  # Max 5 concurrent operations
        
        async def rate_limited_operation(item):
            async with semaphore:
                await asyncio.sleep(0.1)  # Simulate work
                return f"Processed {item}"
        
        # Process many items with limited concurrency
        items = range(20)
        tasks = [rate_limited_operation(item) for item in items]
        results = await asyncio.gather(*tasks)
        
        # 2. Use asyncio.as_completed() for processing results as they arrive
        async def process_as_completed():
            tasks = [asyncio.sleep(i * 0.1) for i in range(5)]
            
            for coro in asyncio.as_completed(tasks):
                result = await coro
                print(f"Task completed: {result}")
        
        await process_as_completed()
        
        return results
    
    # Run all best practices examples
    return await asyncio.gather(
        correct_async_patterns(),
        avoid_common_pitfalls(),
        performance_optimization()
    )

# Example of how to run the complete asyncio examples
async def run_all_asyncio_examples():
    """Run all asyncio examples"""
    
    print("=== Basic Async Operations ===")
    await understanding_async_basics()
    
    print("\n=== Concurrent HTTP Requests ===")
    await concurrent_http_requests()
    
    print("\n=== Task Management ===")
    await task_management_patterns()
    
    print("\n=== Producer-Consumer Pattern ===")
    await producer_consumer_pattern()
    
    print("\n=== Data Pipeline ===")
    await run_data_pipeline_example()
    
    print("\n=== Error Handling ===")
    await error_handling_patterns()
    
    print("\n=== Best Practices ===")
    await asyncio_best_practices()
    
    return "All asyncio examples completed"

# To run: asyncio.run(run_all_asyncio_examples())
```