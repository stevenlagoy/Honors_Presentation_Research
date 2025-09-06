def main() -> None:
    with open("D:\\data\\test.txt",'w') as file:
        print("opened!")
        file.write("Hello!")

if __name__ == "__main__":
    main()