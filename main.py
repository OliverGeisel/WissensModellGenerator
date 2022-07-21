import gui


def run():
    window = gui.create_main()
    event, window = gui.run_main(window)
    if event == "new-knowledge":
        gui.run_new_knowledge(window)


if __name__ == "__main__":
    run()
