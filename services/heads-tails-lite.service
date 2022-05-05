[Unit]
Description=heads-tails-lite
After=network.target pigpiod.service

[Service]
Type=simple
ExecStart=/usr/bin/python3 /home/heads-tails/heads-tails-lite/python/heads-tails-lite.py
RestartSec=5
Restart=always
TimeoutSec=10

[Install]
WantedBy=multi-user.target