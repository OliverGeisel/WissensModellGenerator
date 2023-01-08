import gui


def run():
    try:
        window = gui.create_main()
        event, window = gui.run_main(window)
        if event == "END":
            pass
        elif event == "new-knowledge":
            gui.run_new_knowledge(window)
        elif event == "new-structure":
            gui.run_new_structure(window)
        elif event == "new-source":
            gui.run_new_source(window)

    except Exception as e:
        input("Fehler! bitte enter drücken!")
        print(e)
    else:
        print("Bye!")


if __name__ == "__main__":
    run()
