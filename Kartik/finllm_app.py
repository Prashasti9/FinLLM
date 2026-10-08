import subprocess
import sys
import os


# ============================================================
# FINLLM MAIN APPLICATION
# ============================================================

BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)


def run_script(script_name):
    """
    Runs another FinLLM component using the
    same Python environment currently running this app.
    """

    script_path = os.path.join(
        BASE_DIR,
        script_name
    )

    if not os.path.exists(script_path):
        print(
            f"\nERROR: {script_name} was not found."
        )

        input(
            "\nPress Enter to return to FinLLM..."
        )

        return

    print(
        f"\nStarting {script_name}...\n"
    )

    subprocess.run(
        [
            sys.executable,
            "-u",
            script_path
        ]
    )

    input(
        "\nPress Enter to return to FinLLM..."
    )


def show_header():

    print(
        "\n========================================"
    )

    print(
        "               FINLLM"
    )

    print(
        "     FINANCIAL INTELLIGENCE SYSTEM"
    )

    print(
        "========================================"
    )


def show_menu():

    print(
        "\n1. Ask Policy Documents"
    )

    print(
        "2. Financial Data Query"
    )

    print(
        "3. Generate Compliance Review"
    )

    print(
        "4. Human Case Decision"
    )

    print(
        "5. Exit"
    )


while True:

    show_header()

    show_menu()

    choice = input(
        "\nSelect option (1-5): "
    ).strip()


    # --------------------------------------------------------
    # 1. DOCUMENT RAG
    # --------------------------------------------------------

    if choice == "1":

        run_script(
            "ask_chunks_v3.py"
        )


    # --------------------------------------------------------
    # 2. FINANCIAL DATABASE
    # --------------------------------------------------------

    elif choice == "2":

        run_script(
            "financial_query_cli.py"
        )


    # --------------------------------------------------------
    # 3. COMPLIANCE REVIEW
    # --------------------------------------------------------

    elif choice == "3":

        run_script(
            "case_compliance_explanation.py"
        )


    # --------------------------------------------------------
    # 4. HUMAN DECISION
    # --------------------------------------------------------

    elif choice == "4":

        run_script(
            "case_decision_cli.py"
        )


    # --------------------------------------------------------
    # 5. EXIT
    # --------------------------------------------------------

    elif choice == "5":

        print(
            "\nFinLLM session ended."
        )

        break


    else:

        print(
            "\nInvalid selection. Choose 1-5."
        )

        input(
            "\nPress Enter to continue..."
        )