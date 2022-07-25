import gui


def run():
    try:
        window = gui.create_main()
        event, window = gui.run_main(window)
        if event == "END":
            pass
        elif event == "new-knowledge":
            gui.run_new_knowledge(window)
    except Exception:
        input("Fehler! bitte enter drücken!")
    else:
        print("Bye!")


if __name__ == "__main__":
    run()
