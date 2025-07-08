"""
Network manager for TCP/IP chess communication
"""

import socket
import threading
import json
import time
from typing import Optional, Callable, Dict, Any

class NetworkManager:
    """Handles TCP/IP communication for networked chess games"""
    
    def __init__(self, on_move_received: Callable = None, on_connection_lost: Callable = None):
        self.socket: Optional[socket.socket] = None
        self.is_server = False
        self.is_connected = False
        self.connection_thread: Optional[threading.Thread] = None
        self.listener_thread: Optional[threading.Thread] = None
        self.on_move_received = on_move_received
        self.on_connection_lost = on_connection_lost
        self.running = False
        
    def start_server(self, port: int = 8888) -> bool:
        """Start as server and wait for connection"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.socket.bind(('0.0.0.0', port))
            self.socket.listen(1)
            self.is_server = True
            self.running = True
            
            print(f"Server started on port {port}, waiting for connection...")
            
            # Start accepting connections in a separate thread
            self.connection_thread = threading.Thread(target=self._accept_connections, daemon=True)
            self.connection_thread.start()
            
            return True
        except Exception as e:
            print(f"Failed to start server: {e}")
            return False
    
    def connect_to_server(self, host: str, port: int = 8888) -> bool:
        """Connect to a server"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((host, port))
            self.is_server = False
            self.is_connected = True
            self.running = True
            
            print(f"Connected to server at {host}:{port}")
            
            # Start listening for messages
            self.listener_thread = threading.Thread(target=self._listen_for_messages, daemon=True)
            self.listener_thread.start()
            
            return True
        except Exception as e:
            print(f"Failed to connect to server: {e}")
            return False
    
    def _accept_connections(self):
        """Accept incoming connections (server only)"""
        try:
            client_socket, address = self.socket.accept()
            print(f"Client connected from {address}")
            
            # Replace server socket with client connection
            self.socket.close()
            self.socket = client_socket
            self.is_connected = True
            
            # Start listening for messages
            self.listener_thread = threading.Thread(target=self._listen_for_messages, daemon=True)
            self.listener_thread.start()
            
        except Exception as e:
            if self.running:
                print(f"Error accepting connection: {e}")
                self._handle_connection_lost()
    
    def _listen_for_messages(self):
        """Listen for incoming messages"""
        while self.running and self.is_connected:
            try:
                data = self.socket.recv(1024)
                if not data:
                    self._handle_connection_lost()
                    break
                
                message = json.loads(data.decode('utf-8'))
                self._handle_message(message)
                
            except Exception as e:
                if self.running:
                    print(f"Error receiving message: {e}")
                    self._handle_connection_lost()
                break
    
    def _handle_message(self, message: Dict[str, Any]):
        """Handle received message"""
        msg_type = message.get('type')
        
        if msg_type == 'move' and self.on_move_received:
            move_data = message.get('data')
            self.on_move_received(move_data)
        elif msg_type == 'chat' and hasattr(self, 'on_chat_received'):
            self.on_chat_received(message.get('data'))
        elif msg_type == 'game_state' and hasattr(self, 'on_game_state_received'):
            self.on_game_state_received(message.get('data'))
    
    def send_move(self, from_pos: tuple, to_pos: tuple, piece_type: str) -> bool:
        """Send a move to the opponent"""
        if not self.is_connected:
            return False
        
        try:
            message = {
                'type': 'move',
                'data': {
                    'from': from_pos,
                    'to': to_pos,
                    'piece': piece_type,
                    'timestamp': time.time()
                }
            }
            
            self.socket.send(json.dumps(message).encode('utf-8'))
            return True
        except Exception as e:
            print(f"Error sending move: {e}")
            self._handle_connection_lost()
            return False
    
    def send_chat_message(self, message: str) -> bool:
        """Send a chat message"""
        if not self.is_connected:
            return False
        
        try:
            msg = {
                'type': 'chat',
                'data': {
                    'message': message,
                    'timestamp': time.time()
                }
            }
            
            self.socket.send(json.dumps(msg).encode('utf-8'))
            return True
        except Exception as e:
            print(f"Error sending chat message: {e}")
            return False
    
    def send_game_state(self, state: Dict[str, Any]) -> bool:
        """Send game state update"""
        if not self.is_connected:
            return False
        
        try:
            message = {
                'type': 'game_state',
                'data': state
            }
            
            self.socket.send(json.dumps(message).encode('utf-8'))
            return True
        except Exception as e:
            print(f"Error sending game state: {e}")
            return False
    
    def _handle_connection_lost(self):
        """Handle lost connection"""
        self.is_connected = False
        if self.on_connection_lost:
            self.on_connection_lost()
    
    def disconnect(self):
        """Disconnect from network"""
        self.running = False
        self.is_connected = False
        
        if self.socket:
            try:
                self.socket.close()
            except:
                pass
            self.socket = None
        
        # Wait for threads to finish
        if self.connection_thread and self.connection_thread.is_alive():
            self.connection_thread.join(timeout=1)
        if self.listener_thread and self.listener_thread.is_alive():
            self.listener_thread.join(timeout=1)
    
    def get_status(self) -> Dict[str, Any]:
        """Get network status"""
        return {
            'connected': self.is_connected,
            'is_server': self.is_server,
            'running': self.running
        }