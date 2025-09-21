#!/usr/bin/env python3
"""
Main entry point for Taskflow services.
Allows running individual services or all services together.
"""

import argparse
import logging
import multiprocessing
import sys
from typing import List

from taskflow.backend.ingestor.service import run_ingestor_cli
from taskflow.backend.extractor.service import run_extractor_service
from taskflow.backend.platform_manager.service import run_platform_manager_service


def run_frontend():
    """Run the Streamlit frontend."""
    import subprocess
    subprocess.run([
        sys.executable, "-m", "streamlit", "run", 
        "taskflow/frontend/app.py",
        "--server.port", "8501"
    ])


def run_service(service_name: str):
    """Run a specific service."""
    services = {
        "ingestor": run_ingestor_cli,
        "extractor": run_extractor_service,
        "platform_manager": run_platform_manager_service,
        "frontend": run_frontend
    }
    
    if service_name not in services:
        print(f"❌ Unknown service: {service_name}")
        print(f"Available services: {', '.join(services.keys())}")
        sys.exit(1)
    
    print(f"🚀 Starting {service_name} service...")
    services[service_name]()


def run_all_services():
    """Run all services in parallel."""
    services = ["extractor", "platform_manager", "frontend"]
    processes: List[multiprocessing.Process] = []
    
    print("🚀 Starting all Taskflow services...")
    
    try:
        # Start backend services
        for service in services:
            process = multiprocessing.Process(target=run_service, args=(service,))
            process.start()
            processes.append(process)
            print(f"✅ Started {service} service (PID: {process.pid})")
        
        print("\n🎉 All services started successfully!")
        print("📊 Frontend available at: http://localhost:8501")
        print("⚠️  Note: Use the frontend ingestor or run 'python -m taskflow.backend.main ingestor' separately")
        print("🛑 Press Ctrl+C to stop all services\n")
        
        # Wait for all processes
        for process in processes:
            process.join()
    
    except KeyboardInterrupt:
        print("\n🛑 Stopping all services...")
        for process in processes:
            if process.is_alive():
                process.terminate()
                process.join()
        print("👋 All services stopped")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Taskflow Agent Services")
    parser.add_argument(
        "service",
        nargs="?",
        choices=["ingestor", "extractor", "platform_manager", "frontend", "all"],
        default="all",
        help="Service to run (default: all)"
    )
    parser.add_argument(
        "--log-level",
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        help="Log level (default: INFO)"
    )
    
    args = parser.parse_args()
    
    # Configure logging
    logging.basicConfig(
        level=getattr(logging, args.log_level),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    
    if args.service == "all":
        run_all_services()
    else:
        run_service(args.service)


if __name__ == "__main__":
    main()