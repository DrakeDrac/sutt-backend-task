import csv
import os

# Custom Exceptions
class RoomNotFoundError(Exception):
    # Error when a room id does not exist.
    pass

class TimeslotAlreadyBookedError(Exception):
    # Error when trying to book an already booked hour.
    pass

class RoomAlreadyExistsError(Exception):
    # Error when trying to create a room that already exists.
    pass

# Room Class
class Room:
    # Represents a single classroom with its booking schedule.
    def __init__(self, room_no, building, capacity):
        self.room_no = room_no
        self.building = building
        self.capacity = capacity
        self.booked_hours = []

    def is_available(self, hour):
        if hour in self.booked_hours:
            return False
        else:
            return True

    def book_hour(self, hour):
        # Books the room for a given hour.
        if not self.is_available(hour):
            raise TimeslotAlreadyBookedError(
                f"Timeslot {hour}:00 is already booked for room {self.room_no}"
            )
        
        self.booked_hours.append(hour)
        self.booked_hours.sort()
        return True

    def display_details(self):
        # Prints the details for this room.
        print(f"- Room Details: {self.room_no} -")
        print(f"  Building: {self.building}")
        print(f"  Capacity: {self.capacity}")
        
        if not self.booked_hours:
            print("  Schedule: This room is free all day.")
        else:
            pretty_hours = []
            for h in self.booked_hours:
                pretty_hours.append(f"{h}:00")
            print(f"  Schedule (Booked Hours): {', '.join(pretty_hours)}")
        print("-----------")


# Helper Functions

def find_room_by_id(all_rooms, room_no):
    # A helper function to find a Room object in a list by its room_no.
    # Returns the Room object or None if not found.
    for room in all_rooms:
        if room.room_no == room_no:
            return room
    return None

def load_rooms_from_csv(filename):
    # Loads all room data from the CSV file when the program starts.
    # This is part of the brownie points.
    all_rooms = []
    
    if not os.path.exists(filename):
        print("Welcome! No existing 'bookings_final_state.csv' file found. Starting fresh.")
        return all_rooms

    print(f"Loading data from '{filename}'...")
    try:
        with open(filename, mode='r', newline='') as file:
            reader = csv.reader(file)
            
            header = next(reader) 
            
            for row in reader:
                room_no = row[0]
                building = row[1]
                capacity = int(row[2])
                booked_hours_str = row[3]
                
                new_room = Room(room_no, building, capacity)
                
                if booked_hours_str:
                    hour_strings = booked_hours_str.split(';')
                    for h_str in hour_strings:
                        new_room.booked_hours.append(int(h_str))
                
                all_rooms.append(new_room)
                
        print(f"Successfully loaded {len(all_rooms)} rooms.")
    except Exception as e:
        print(f"Error loading file: {e}. Starting with an empty system.")
        return []
        
    return all_rooms

def save_rooms_to_csv(filename, all_rooms):
    # Saves the final state of all rooms to a csv file.
    print(f"Saving data to '{filename}'...")
    try:
        with open(filename, mode='w', newline='') as file:
            writer = csv.writer(file)
            
            writer.writerow(["room_no", "building", "capacity", "booked_hours"])
            
            for room in all_rooms:
                hour_strings = []
                for h in room.booked_hours:
                    hour_strings.append(str(h))
                booked_hours_str = ";".join(hour_strings)
                
                writer.writerow([
                    room.room_no, 
                    room.building, 
                    room.capacity, 
                    booked_hours_str
                ])
        print("Data saved successfully.")
    except Exception as e:
        print(f"Error saving data: {e}")


# Main Functionality Handlers

def handle_create_room(all_rooms):
    # Adds new room details.
    print("\n- Create a New Room -")
    room_no = input("Enter Room No. (e.g., '6101'): ")
    
    if find_room_by_id(all_rooms, room_no) is not None:
        raise RoomAlreadyExistsError(f"Room with ID '{room_no}' already exists.")
        
    building = input("Enter Building Name (e.g., 'NAB'): ")
    
    try:
        capacity = int(input("Enter Capacity (e.g., 50): "))
    except ValueError:
        print("Error: Capacity must be a number.")
        return

    new_room = Room(room_no, building, capacity)
    all_rooms.append(new_room)
    print(f"Success: Room '{room_no}' created in {building}.")

def handle_book_room(all_rooms):
    # Asks user for a room and hour to book.
    print("\n- Book a Room -")
    room_no = input("Enter Room No. to book: ")
    
    room = find_room_by_id(all_rooms, room_no)
    
    if room is None:
        raise RoomNotFoundError(f"Room with ID '{room_no}' was not found.")
    
    try:
        hour = int(input("Enter hour to book (0-23): "))
        if not (0 <= hour <= 23):
            print("Error: Hour must be between 0 and 23.")
            return
    except ValueError:
        print("Error: Hour must be a number.")
        return

    room.book_hour(hour)
    print(f"Success: Room '{room_no}' has been booked for {hour}:00.")

def handle_find_rooms(all_rooms):
    # Lets user search for rooms based on different filters.
    print("\n- Find Available Rooms -")
    print("Enter search criteria (leave blank to skip a filter):")
    
    filter_building = input("Filter by building: ")
    filter_capacity_str = input("Filter by minimum capacity: ")
    filter_hour_str = input("Filter by hour available (0-23): ")
    
    results = []
    
    for room in all_rooms:
        matches = True
        
        # 1. Check building filter
        if filter_building and room.building != filter_building:
            matches = False
            
        # 2. Check capacity filter
        if filter_capacity_str:
            try:
                min_capacity = int(filter_capacity_str)
                if room.capacity < min_capacity:
                    matches = False
            except ValueError:
                print("Invalid capacity input.")
                
        # 3. Check availability filter
        if filter_hour_str:
            try:
                hour = int(filter_hour_str)
                if not (0 <= hour <= 23):
                    print("Invalid hour.")
                elif not room.is_available(hour):
                    matches = False
            except ValueError:
                print("Invalid hour input.")
        
        if matches:
            results.append(room)

    if not results:
        print("\nNo rooms found.")
    else:
        print(f"\nFound {len(results)} matching rooms:")
        for room in results:
            room.display_details()

def handle_view_schedule(all_rooms):
    # Displays the details and schedule for a specific room.
    print("\n- View Room Schedule -")
    room_no = input("Enter Room No. to view: ")
    
    room = find_room_by_id(all_rooms, room_no)
    
    if room is None:
        raise RoomNotFoundError(f"Room with id '{room_no}' was not found.")
        
    room.display_details()


csv_filename = "data.csv"

all_rooms = load_rooms_from_csv(csv_filename)

while True:
    print("\n- Classroom Booking System")
    print("What would you like to do?")
    print("  1. Create a new room")
    print("  2. Book a room")
    print("  3. Find available rooms")
    print("  4. View a room's schedule")
    print("  5. Exit")
    
    choice = input("Enter your choice (1-5): ")
    
    try:
        if choice == '1':
            handle_create_room(all_rooms)
            
        elif choice == '2':
            handle_book_room(all_rooms)
            
        elif choice == '3':
            handle_find_rooms(all_rooms)
            
        elif choice == '4':
            handle_view_schedule(all_rooms)
            
        elif choice == '5':
            save_rooms_to_csv(csv_filename, all_rooms)
            print("Goodbye!")
            break
            
        else:
            print("Invalid choice. Please enter a number from 1 to 5.")
    
    except (RoomNotFoundError, TimeslotAlreadyBookedError, RoomAlreadyExistsError) as e:
        print(f"\nError: {e}")
    except Exception as e:
        print(f"\nAn error occurred: {e}")
    
    input("\nPress Enter to continue...")
