import socket
import csv
import datetime

HOST = "0.0.0.0"  # Listen on all available network interfaces
PORT = 5001       # Must match the Arduino's serverPort

# Create the server socket (IPv4, TCP)
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind((HOST, PORT))
server_socket.listen(1)

print(f"Listening for connections on port {PORT}...")

client_socket, client_address = server_socket.accept()
print(f"Connected to {client_address}")

csv_filename = "sensor_data_pull.csv"
exercise_name = "Pull"

# Open CSV file to store sensor data
with open(csv_filename, mode="w", newline="") as file:
    writer = csv.writer(file)
    # Write header
    writer.writerow([
        "Timestamp",
        "Acce_x", "Acce_y", "Acce_z",
        "Gyro_x", "Gyro_y", "Gyro_z",
        "Label"
    ])

    try:
        while True:
            # Receive data from the client
            data = client_socket.recv(1024).decode("utf-8").strip()
            if not data:
                continue

            # Split incoming string into columns
            # data should look like: "Ax,Ay,Az,Gx,Gy,Gz"
            sensor_values = data.split(",")
            if len(sensor_values) != 6:
                # Invalid data format, skip
                continue

            # 1) Create a timestamp
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")

            # 2) Write row to CSV, label is left blank (or "TBD")
            row = [
                timestamp,
                sensor_values[0],  # Acce_x
                sensor_values[1],  # Acce_y
                sensor_values[2],  # Acce_z
                sensor_values[3],  # Gyro_x
                sensor_values[4],  # Gyro_y
                sensor_values[5],  # Gyro_z
                exercise_name      # Label (to fill later)
            ]
            writer.writerow(row)
            file.flush()  # Ensure data is written immediately

            print(f"Received: {row}")

    except KeyboardInterrupt:
        print("Server stopped by user.")
    finally:
        client_socket.close()
        server_socket.close()
