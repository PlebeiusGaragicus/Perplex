#!/usr/bin/env python3
"""
Script to check if Ollama is running and provide instructions for installing and starting it.
"""
from src.utils.ollama_check import check_and_print_status

if __name__ == "__main__":
    check_and_print_status()
