#!/bin/sh
# Compiles and runs the firmware logic tests on a PC (Linux/macOS, or Windows
# with MSYS2/WSL). Needs g++ or clang++.
set -e
cd "$(dirname "$0")"
mkdir -p build
${CXX:-g++} -std=c++17 -Wall -Wextra -O1 -o build/test_logic test_logic.cpp
./build/test_logic
