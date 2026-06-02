#!/usr/bin/env python3
import subprocess
import sys
import termios
import tty


TOPIC = "/model/dem_level_vehicle/cmd_vel"
TWISTS = {
    "\x1b[A": "linear: {x: 1.2}",
    "\x1b[B": "linear: {x: -0.8}",
    "\x1b[D": "angular: {z: 0.8}",
    "\x1b[C": "angular: {z: -0.8}",
    " ": "linear: {x: 0.0}, angular: {z: 0.0}",
}


def main():
    print("Arrow keys drive dem_level_vehicle. Space stops. Q quits.")
    old_settings = termios.tcgetattr(sys.stdin)
    try:
        tty.setraw(sys.stdin.fileno())
        while True:
            key = read_key()
            if key.lower() == "q":
                publish_twist(TWISTS[" "])
                break
            if key in TWISTS:
                publish_twist(TWISTS[key])
    finally:
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)


def read_key():
    key = sys.stdin.read(1)
    if key == "\x1b":
        key += sys.stdin.read(2)
    return key


def publish_twist(message):
    subprocess.run(
        [
            "gz",
            "topic",
            "-t",
            TOPIC,
            "-m",
            "gz.msgs.Twist",
            "-p",
            message,
        ],
        check=False,
    )


if __name__ == "__main__":
    main()
