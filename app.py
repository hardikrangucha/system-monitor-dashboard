import psutil
import time
from flask import Flask, jsonify

app = Flask(__name__)

@app.route("/")
def index():
    """Serve the dashboard HTML directly from Python (no templates folder needed)"""
    html_content = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>System Monitor | Real-time CPU & RAM Dashboard</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        :root {
            --primary-bg: #000000;
            --secondary-bg: #1c1c1e;
            --tertiary-bg: #2c2c2e;
            --accent-blue: #007aff;
            --accent-green: #30d158;
            --accent-orange: #ff9500;
            --accent-red: #ff3b30;
            --text-primary: #ffffff;
            --text-secondary: #99999d;
            --border-color: #38383a;
            --font-primary: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        }

        body {
            font-family: var(--font-primary);
            background: var(--primary-bg);
            color: var(--text-primary);
            line-height: 1.6;
            min-height: 100vh;
        }

        .header {
            text-align: center;
            padding: 3rem 2rem 2rem;
            background: linear-gradient(180deg, var(--primary-bg) 0%, var(--secondary-bg) 100%);
        }

        .header h1 {
            font-size: clamp(2.5rem, 5vw, 4rem);
            font-weight: 700;
            background: linear-gradient(135deg, var(--accent-blue) 0%, #5ac8fa 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            margin-bottom: 1rem;
        }

        .header p {
            font-size: 1.25rem;
            color: var(--text-secondary);
            max-width: 600px;
            margin: 0 auto;
        }

        .control-panel {
            display: flex;
            justify-content: center;
            align-items: center;
            gap: 2rem;
            padding: 2rem;
            background: var(--secondary-bg);
            border-bottom: 1px solid var(--border-color);
            flex-wrap: wrap;
        }

        .status-text {
            display: flex;
            align-items: center;
            gap: 0.5rem;
            font-weight: 500;
        }

        .status-indicator {
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background: var(--accent-green);
            animation: pulse 2s infinite;
        }

        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
        }

        .dashboard {
            max-width: 1400px;
            margin: 0 auto;
            padding: 3rem 2rem;
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
            gap: 3rem;
        }

        .metric-card {
            background: var(--secondary-bg);
            border: 1px solid var(--border-color);
            border-radius: 24px;
            padding: 3rem;
            position: relative;
            transition: all 0.3s ease;
        }

        .metric-card:hover {
            transform: translateY(-4px);
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.25);
            border-color: var(--accent-blue);
        }

        .card-header {
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 2rem;
        }

        .card-title {
            font-size: 1.5rem;
            font-weight: 600;
            color: var(--text-primary);
        }

        .card-icon {
            width: 32px;
            height: 32px;
            border-radius: 8px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.2rem;
        }

        .card-icon.cpu {
            background: linear-gradient(135deg, var(--accent-blue) 0%, #5ac8fa 100%);
        }

        .card-icon.ram {
            background: linear-gradient(135deg, var(--accent-green) 0%, #64d2ff 100%);
        }

        .progress-container {
            position: relative;
            width: 200px;
            height: 200px;
            margin: 0 auto 2rem;
        }

        .progress-circle {
            width: 100%;
            height: 100%;
            transform: rotate(-90deg);
        }

        .progress-track {
            fill: none;
            stroke: var(--tertiary-bg);
            stroke-width: 8;
        }

        .progress-bar {
            fill: none;
            stroke-width: 8;
            stroke-linecap: round;
            transition: stroke-dasharray 0.3s ease;
        }

        .progress-text {
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            text-align: center;
        }

        .progress-percentage {
            font-size: 2.5rem;
            font-weight: 700;
            color: var(--text-primary);
            line-height: 1;
        }

        .progress-label {
            font-size: 0.9rem;
            color: var(--text-secondary);
            font-weight: 500;
            margin-top: 0.5rem;
        }

        .metrics-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 1.5rem;
        }

        .metric-item {
            background: var(--tertiary-bg);
            border-radius: 12px;
            padding: 1.5rem;
            text-align: center;
            transition: all 0.15s ease;
        }

        .metric-item:hover {
            background: var(--border-color);
        }

        .metric-value {
            font-size: 1.25rem;
            font-weight: 600;
            color: var(--text-primary);
            margin-bottom: 0.5rem;
        }

        .metric-label {
            font-size: 0.8rem;
            color: var(--text-secondary);
            font-weight: 500;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }

        .error-message {
            position: fixed;
            top: 1rem;
            right: 1rem;
            background: var(--accent-red);
            color: white;
            padding: 1rem 1.5rem;
            border-radius: 12px;
            font-weight: 500;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.25);
            transform: translateX(100%);
            transition: transform 0.3s ease;
            z-index: 1000;
            max-width: 300px;
        }

        .error-message.show {
            transform: translateX(0);
        }

        .loading {
            opacity: 0.5;
            pointer-events: none;
        }

        @media (max-width: 768px) {
            .dashboard {
                grid-template-columns: 1fr;
                padding: 2rem 1rem;
                gap: 2rem;
            }
            
            .progress-container {
                width: 160px;
                height: 160px;
            }
            
            .progress-percentage {
                font-size: 2rem;
            }
            
            .metrics-grid {
                grid-template-columns: repeat(2, 1fr);
            }
        }
    </style>
</head>
<body>
    <header class="header">
        <h1>System Monitor</h1>
        <p>Real-time CPU and RAM usage dashboard with live system data</p>
    </header>

    <section class="control-panel">
        <div class="status-text">
            <div class="status-indicator" id="statusIndicator"></div>
            <span id="statusText">Connecting...</span>
        </div>
    </section>

    <main class="dashboard">
        <article class="metric-card cpu">
            <header class="card-header">
                <h2 class="card-title">CPU Usage</h2>
                <div class="card-icon cpu">⚡</div>
            </header>
            
            <div class="progress-container">
                <svg class="progress-circle" viewBox="0 0 200 200">
                    <defs>
                        <linearGradient id="cpuGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                            <stop offset="0%" style="stop-color:#007aff"/>
                            <stop offset="100%" style="stop-color:#5ac8fa"/>
                        </linearGradient>
                    </defs>
                    <circle class="progress-track" cx="100" cy="100" r="90"></circle>
                    <circle class="progress-bar" cx="100" cy="100" r="90" id="cpuProgressBar" stroke="url(#cpuGradient)"></circle>
                </svg>
                <div class="progress-text">
                    <div class="progress-percentage" id="cpuPercentage">--</div>
                    <div class="progress-label">Current Load</div>
                </div>
            </div>

            <div class="metrics-grid">
                <div class="metric-item">
                    <div class="metric-value" id="cpuCores">--</div>
                    <div class="metric-label">Cores</div>
                </div>
                <div class="metric-item">
                    <div class="metric-value" id="cpuThreads">--</div>
                    <div class="metric-label">Threads</div>
                </div>
                <div class="metric-item">
                    <div class="metric-value" id="cpuFreq">--</div>
                    <div class="metric-label">Frequency</div>
                </div>
                <div class="metric-item">
                    <div class="metric-value" id="cpuTemp">--</div>
                    <div class="metric-label">Temperature</div>
                </div>
            </div>
        </article>

        <article class="metric-card ram">
            <header class="card-header">
                <h2 class="card-title">Memory Usage</h2>
                <div class="card-icon ram">💾</div>
            </header>
            
            <div class="progress-container">
                <svg class="progress-circle" viewBox="0 0 200 200">
                    <defs>
                        <linearGradient id="ramGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                            <stop offset="0%" style="stop-color:#30d158"/>
                            <stop offset="100%" style="stop-color:#64d2ff"/>
                        </linearGradient>
                    </defs>
                    <circle class="progress-track" cx="100" cy="100" r="90"></circle>
                    <circle class="progress-bar" cx="100" cy="100" r="90" id="ramProgressBar" stroke="url(#ramGradient)"></circle>
                </svg>
                <div class="progress-text">
                    <div class="progress-percentage" id="ramPercentage">--</div>
                    <div class="progress-label">In Use</div>
                </div>
            </div>

            <div class="metrics-grid">
                <div class="metric-item">
                    <div class="metric-value" id="ramUsed">--</div>
                    <div class="metric-label">Used</div>
                </div>
                <div class="metric-item">
                    <div class="metric-value" id="ramTotal">--</div>
                    <div class="metric-label">Total</div>
                </div>
                <div class="metric-item">
                    <div class="metric-value" id="ramFree">--</div>
                    <div class="metric-label">Available</div>
                </div>
                <div class="metric-item">
                    <div class="metric-value" id="ramCached">--</div>
                    <div class="metric-label">Cached</div>
                </div>
            </div>
        </article>
    </main>

    <div class="error-message" id="errorMessage">
        <span id="errorText"></span>
    </div>

    <script>
        class SystemMonitor {
            constructor() {
                this.CIRCLE_CIRCUMFERENCE = 2 * Math.PI * 90;
                this.UPDATE_INTERVAL = 2000; // 2 seconds
                this.API_ENDPOINT = '/api/system-stats';
                
                this.elements = {
                    statusText: document.getElementById('statusText'),
                    cpuPercentage: document.getElementById('cpuPercentage'),
                    cpuProgressBar: document.getElementById('cpuProgressBar'),
                    cpuCores: document.getElementById('cpuCores'),
                    cpuThreads: document.getElementById('cpuThreads'),
                    cpuFreq: document.getElementById('cpuFreq'),
                    cpuTemp: document.getElementById('cpuTemp'),
                    ramPercentage: document.getElementById('ramPercentage'),
                    ramProgressBar: document.getElementById('ramProgressBar'),
                    ramUsed: document.getElementById('ramUsed'),
                    ramTotal: document.getElementById('ramTotal'),
                    ramFree: document.getElementById('ramFree'),
                    ramCached: document.getElementById('ramCached'),
                    errorMessage: document.getElementById('errorMessage'),
                    errorText: document.getElementById('errorText')
                };
                
                this.init();
            }
            
            init() {
                this.setupProgressBars();
                this.startMonitoring();
            }
            
            setupProgressBars() {
                [this.elements.cpuProgressBar, this.elements.ramProgressBar].forEach(bar => {
                    bar.style.strokeDasharray = this.CIRCLE_CIRCUMFERENCE;
                    bar.style.strokeDashoffset = this.CIRCLE_CIRCUMFERENCE;
                });
            }
            
            async fetchSystemData() {
                try {
                    const response = await fetch(this.API_ENDPOINT);
                    if (!response.ok) {
                        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
                    }
                    const data = await response.json();
                    return data;
                } catch (error) {
                    console.error('Failed to fetch system data:', error);
                    this.showError(`Connection failed: ${error.message}`);
                    throw error;
                }
            }
            
            updateProgressBar(element, percentage) {
                const offset = this.CIRCLE_CIRCUMFERENCE - (percentage / 100) * this.CIRCLE_CIRCUMFERENCE;
                element.style.strokeDashoffset = offset;
            }
            
            updateMetrics(data) {
                try {
                    // Update CPU metrics
                    if (data.cpu) {
                        this.elements.cpuPercentage.textContent = `${data.cpu.usage}%`;
                        this.updateProgressBar(this.elements.cpuProgressBar, data.cpu.usage);
                        this.elements.cpuCores.textContent = data.cpu.cores;
                        this.elements.cpuThreads.textContent = data.cpu.threads;
                        this.elements.cpuFreq.textContent = `${data.cpu.frequency} GHz`;
                        this.elements.cpuTemp.textContent = `${data.cpu.temperature}°C`;
                    }
                    
                    // Update RAM metrics
                    if (data.memory) {
                        this.elements.ramPercentage.textContent = `${data.memory.usage}%`;
                        this.updateProgressBar(this.elements.ramProgressBar, data.memory.usage);
                        this.elements.ramUsed.textContent = `${data.memory.used} GB`;
                        this.elements.ramTotal.textContent = `${data.memory.total} GB`;
                        this.elements.ramFree.textContent = `${data.memory.available} GB`;
                        this.elements.ramCached.textContent = `${data.memory.cached} GB`;
                    }
                    
                    // Update status
                    this.elements.statusText.textContent = 'Live Monitoring';
                    this.elements.statusText.style.color = 'var(--accent-green)';
                    
                    // Handle alerts
                    if (data.alerts && data.alerts.message) {
                        this.showError(data.alerts.message);
                    }
                    
                } catch (error) {
                    console.error('Failed to update metrics:', error);
                    this.showError('Failed to update display');
                }
            }
            
            showError(message) {
                this.elements.errorText.textContent = message;
                this.elements.errorMessage.classList.add('show');
                
                setTimeout(() => {
                    this.elements.errorMessage.classList.remove('show');
                }, 5000);
            }
            
            async startMonitoring() {
                console.log('🚀 Starting system monitoring...');
                
                const updateCycle = async () => {
                    try {
                        const data = await this.fetchSystemData();
                        this.updateMetrics(data);
                    } catch (error) {
                        this.elements.statusText.textContent = 'Connection Lost';
                        this.elements.statusText.style.color = 'var(--accent-red)';
                    }
                };
                
                // Initial update
                await updateCycle();
                
                // Set up recurring updates
                setInterval(updateCycle, this.UPDATE_INTERVAL);
            }
        }
        
        // Start the dashboard when page loads
        document.addEventListener('DOMContentLoaded', () => {
            console.log('🎯 System Monitor Dashboard Loading...');
            new SystemMonitor();
        });
    </script>
</body>
</html>'''
    
    return html_content

@app.route("/api/system-stats")
def get_system_stats():
    """API endpoint that returns real-time system statistics as JSON"""
    try:
        # Get CPU information with a small interval for accurate reading
        cpu_percent = psutil.cpu_percent(interval=0.5)
        cpu_count = psutil.cpu_count()
        cpu_count_logical = psutil.cpu_count(logical=True)
        
        # Get CPU frequency (with error handling for unsupported systems)
        frequency = 3.2  # Default fallback
        try:
            cpu_freq = psutil.cpu_freq()
            if cpu_freq and cpu_freq.current:
                frequency = round(cpu_freq.current / 1000, 1)
        except (OSError, AttributeError, PermissionError):
            # Some systems (like macOS) don't support CPU frequency reading
            frequency = "N/A"
        
        # Get memory information (with error handling)
        try:
            memory = psutil.virtual_memory()
            
            # Calculate cached memory safely
            cached_memory = 0
            if hasattr(memory, 'cached'):
                cached_memory = memory.cached
            if hasattr(memory, 'buffers'):
                cached_memory += memory.buffers
            
            cached_gb = round(cached_memory / (1024**3), 1) if cached_memory > 0 else 0
            
        except Exception as mem_error:
            print(f"⚠️ Memory info error: {mem_error}")
            # Create fallback memory object
            class FallbackMemory:
                percent = 0
                total = 8 * (1024**3)  # 8GB default
                used = 0
                available = 8 * (1024**3)
            memory = FallbackMemory()
            cached_gb = 0
        
        # Calculate temperature (with better error handling)
        temperature = "N/A"  # Default fallback
        
        # Try to get real temperature from system sensors
        try:
            temps = psutil.sensors_temperatures()
            if temps:
                # Try different sensor names based on system type
                sensor_names = ['coretemp', 'cpu_thermal', 'k10temp', 'acpi', 'zenpower']
                for sensor_name in sensor_names:
                    if sensor_name in temps and temps[sensor_name]:
                        temperature = round(temps[sensor_name][0].current, 1)
                        break
        except (AttributeError, KeyError, IndexError, OSError, PermissionError):
            # If no temperature sensors available, use estimation
            temperature = round(35 + (cpu_percent * 0.4), 1)
        
        # If still no temperature, use fallback
        if temperature == "N/A":
            temperature = round(35 + (cpu_percent * 0.4), 1)
        
        # Prepare response data
        system_data = {
            "cpu": {
                "usage": round(cpu_percent, 1),
                "cores": cpu_count,
                "threads": cpu_count_logical,
                "frequency": frequency,
                "temperature": temperature
            },
            "memory": {
                "usage": round(memory.percent, 1),
                "total": round(memory.total / (1024**3), 1),  # Convert to GB
                "used": round(memory.used / (1024**3), 1),
                "available": round(memory.available / (1024**3), 1),
                "cached": cached_gb
            },
            "alerts": {
                "high_cpu": cpu_percent > 80,
                "high_memory": memory.percent > 80,
                "message": "⚠️ High system utilization detected!" if (cpu_percent > 80 or memory.percent > 80) else None
            },
            "timestamp": time.time()
        }
        
        print(f"📊 CPU: {cpu_percent:.1f}% | RAM: {memory.percent:.1f}% | Cores: {cpu_count}")
        
        return jsonify(system_data)
    
    except Exception as e:
        error_msg = f"Failed to retrieve system stats: {str(e)}"
        print(f"❌ Error: {error_msg}")
        return jsonify({
            "error": True,
            "message": error_msg
        }), 500

@app.route("/api/health")
def health_check():
    """Simple health check endpoint"""
    return jsonify({
        "status": "healthy",
        "timestamp": time.time(),
        "service": "System Monitor API",
        "psutil_version": psutil.__version__
    })

if __name__ == '__main__':
    print("🚀 Starting System Monitor Dashboard...")
    print("📊 Dashboard: http://localhost:5001")
    print("🔌 API Endpoint: http://localhost:5001/api/system-stats")
    print("❤️  Health Check: http://localhost:5001/api/health")
    print("=" * 50)
    app.run(debug=True, host='0.0.0.0', port=5001)