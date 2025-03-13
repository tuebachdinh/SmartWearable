import socket
import csv
import datetime
import joblib


# Server settings
HOST = "0.0.0.0"  # Listens on all available interfaces
PORT = 5001  # Must match Arduino's serverPort
# print(datetime.datetime.now())
# Create a socket (IPv4, TCP)
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR,1)  # Allow reusing the same port
server_socket.bind((HOST, PORT))
server_socket.listen(1)
print(f"Listening for connections on port {PORT}...")

# Accept connection
client_socket, client_address = server_socket.accept()
print(f"Connected to {client_address}")

# Open CSV file for writing data
csv_filename = "./saving_data/training_sensor_data_1.csv"
with open(csv_filename, mode="w", newline="") as file:
    writer = csv.writer(file)
    writer.writerow(["Timestamp", "Sensor Value", "label"])  # Write header

    try:
        while True:
            data = client_socket.recv(1024).decode("utf-8").strip()
            if data:
                timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                print(f"Received: {data}")
                data = data.split(',')[0]
                # Save to CSV
                writer.writerow([timestamp, data, "pressed"]) # add the label here
                file.flush()  # Ensure data is written immediately
    except KeyboardInterrupt:
        print("Server stopped.")
    finally:
        client_socket.close()
        server_socket.close()
