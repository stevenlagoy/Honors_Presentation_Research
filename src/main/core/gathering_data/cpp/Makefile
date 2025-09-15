CC = g++
CFLAGS = -std=c++17 -Wall -Wextra -g
OBJS = MapEntity.o State.o County.o main.o

TARGET = main.exe

all: $(TARGET) run clean

$(TARGET): $(OBJS)
	$(CC) $(CFLAGS) -o $(TARGET) $(OBJS)

%.o: %.cpp
	$(CC) $(CFLAGS) -c $< -o $@

run: $(TARGET)
	$(TARGET)

clean:
	del /Q $(OBJS) $(TARGET)