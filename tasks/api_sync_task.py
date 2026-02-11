"""
API Sync Task for KashtawaOS
Sends accumulated sensor data to remote API
"""

import urequests
import json
import gc

class ApiSyncTask:
    """Task for synchronizing logged data with remote API"""
    
    def __init__(self, storage_driver, wifi_task, batch_size=10):
        """
        Initialize API sync task
        
        Args:
            storage_driver: InternalStorageDriver instance
            wifi_task: WiFiTask instance to check connection
            batch_size: Number of readings to accumulate before sending
        """
        self.storage = storage_driver
        self.wifi_task = wifi_task
        self.batch_size = batch_size
        self.last_sent_count = 0
        self.total_sent = 0
        self.send_errors = 0
        
        # API Configuration
        self.api_url = "https://www.fontsistemascr.com/PocketAssets/DemoPI/PocketAssetsWA/PocketAssetsWS/api/RFID/RegisterTagRead"
        self.api_key = "RfidDroneTest"
        
        print(f"[API Sync] Initialized (batch size: {batch_size})")
        print(f"[API Sync] Endpoint: {self.api_url}")
        
    def check_and_send(self):
        """Check if we have enough data to send and sync with API"""
        try:
            # Check WiFi connection first
            if not self.wifi_task.wifi.is_connected():
                print("[API Sync] WiFi not connected, skipping sync")
                return
                
            # Get current line count
            current_count = self.storage.get_line_count()
            
            # Calculate how many new entries we have
            new_entries = current_count - self.last_sent_count
            
            if new_entries >= self.batch_size:
                print(f"[API Sync] Found {new_entries} new entries, sending to API...")
                self._send_batch(new_entries)
            else:
                print(f"[API Sync] Waiting for more data ({new_entries}/{self.batch_size})")
                
        except Exception as e:
            print(f"[API Sync] Error checking data: {e}")
            
    def _send_batch(self, count):
        """
        Send a batch of readings to the API
        
        Args:
            count: Number of readings to send
        """
        import time
        
        try:
            # Read the unsent data (last N entries)
            data_list = self.storage.read_json_lines(count)
            
            if not data_list:
                print("[API Sync] No data to send")
                return
                
            print(f"[API Sync] Preparing to send {len(data_list)} readings...")
            
            # Send each reading to the API
            success_count = 0
            for i, data in enumerate(data_list):
                if self._send_single_reading(data):
                    success_count += 1
                else:
                    print(f"[API Sync] Failed to send reading {i+1}/{len(data_list)}")
                
                # Small delay between requests to avoid overwhelming the server
                if i < len(data_list) - 1:  # Don't delay after last one
                    time.sleep(0.5)  # 500ms delay between requests
                    
            # Update counters
            if success_count > 0:
                self.last_sent_count += success_count
                self.total_sent += success_count
                print(f"[API Sync]  Successfully sent {success_count}/{len(data_list)} readings")
                print(f"[API Sync] Total sent: {self.total_sent}")
            else:
                print(f"[API Sync]  Failed to send batch")
                self.send_errors += 1
                
            # Free memory
            gc.collect()
            
        except Exception as e:
            print(f"[API Sync] Error sending batch: {e}")
            self.send_errors += 1
            
    def _send_single_reading(self, data, max_retries=3):
        """
        Send a single reading to the API with retry logic
        
        Args:
            data: Dictionary with reading data
            max_retries: Maximum number of retry attempts
            
        Returns:
            True if successful, False otherwise
        """
        import time
        
        for attempt in range(max_retries):
            try:
                # Prepare headers
                headers = {
                    'Content-Type': 'application/json',
                    'X-API-Key': self.api_key
                }
                
                # Convert data to JSON
                json_data = json.dumps(data)
                
                # Send POST request
                response = urequests.post(
                    self.api_url,
                    headers=headers,
                    data=json_data
                )
                
                # Check response
                if response.status_code == 200 or response.status_code == 201:
                    # Get response body
                    try:
                        response_text = response.text
                        print(f"[API Sync]  Sent: {data}")
                        print(f"[API Sync]   Server response: {response_text}")
                    except:
                        print(f"[API Sync]  Sent: {data}")
                        print(f"[API Sync]   Server response: OK (no body)")
                    response.close()
                    return True
                else:
                    print(f"[API Sync]  API error {response.status_code}: {response.text}")
                    response.close()
                    
                    # Retry on 5xx errors (server errors)
                    if response.status_code >= 500 and attempt < max_retries - 1:
                        time.sleep(1)  # Wait 1 second before retry
                        print(f"[API Sync] Retrying... (attempt {attempt + 2}/{max_retries})")
                        continue
                    return False
                    
            except OSError as e:
                # Network errors (ECONNABORTED, etc.)
                if attempt < max_retries - 1:
                    print(f"[API Sync]  Network error (attempt {attempt + 1}/{max_retries}): {e}")
                    time.sleep(2)  # Wait 2 seconds before retry
                    print(f"[API Sync] Retrying...")
                else:
                    print(f"[API Sync]  Request failed after {max_retries} attempts: {e}")
                    return False
                    
            except Exception as e:
                print(f"[API Sync]  Request error: {e}")
                return False
        
        return False
            
    def get_sync_stats(self):
        """
        Get synchronization statistics
        
        Returns:
            Dictionary with sync statistics
        """
        try:
            total_readings = self.storage.get_line_count()
            pending = total_readings - self.last_sent_count
            
            return {
                'total_sent': self.total_sent,
                'last_sent_count': self.last_sent_count,
                'pending': pending,
                'send_errors': self.send_errors,
                'wifi_connected': self.wifi_task.wifi.is_connected()
            }
        except Exception as e:
            print(f"[API Sync] Stats error: {e}")
            return None
            
    def force_sync(self):
        """Force synchronization of all pending data"""
        try:
            total_readings = self.storage.get_line_count()
            pending = total_readings - self.last_sent_count
            
            if pending > 0:
                print(f"[API Sync] Force sync: {pending} pending readings")
                self._send_batch(pending)
            else:
                print("[API Sync] No pending data to sync")
                
        except Exception as e:
            print(f"[API Sync] Force sync error: {e}")
            
    def reset_sync_counter(self):
        """Reset the sync counter (useful after clearing log)"""
        self.last_sent_count = 0
        self.total_sent = 0
        self.send_errors = 0
        print("[API Sync] Counters reset")
