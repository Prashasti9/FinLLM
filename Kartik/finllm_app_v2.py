import subprocess
import sys


# ============================================================
# FINLLM MAIN APPLICATION V2
# ============================================================

def run_script(script_name):

    print(
        f"\nStarting {script_name}...\n"
    )

    try:

        result = subprocess.run(
            [
                sys.executable,
                "-u",
                script_name
            ]
        )

        if result.returncode != 0:

            print(
                f"\n{script_name} ended with an error."
            )

        else:

            print(
                f"\n{script_name} finished."
            )

    except FileNotFoundError:

        print(
            f"\nCould not find {script_name}."
        )

    except KeyboardInterrupt:

        print(
            "\nOperation cancelled."
        )


# ============================================================
# MAIN MENU LOOP
# ============================================================

while True:

    print(
        "\n=========================================="
    )

    print(
        "                 FINLLM"
    )

    print(
        "       FINANCIAL INTELLIGENCE SYSTEM"
    )

    print(
        "==========================================\n"
    )

    print(
        "1. Ask Policy Documents"
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
        "5. Run Investigation Agent"
    )

    print(
        "6. Run Full Case Pipeline"
    )

    print(
        "7. Exit"
    )

    choice = input(
        "\nSelect option (1-7): "
    ).strip()


    # ========================================================
    # OPTION 1 — DOCUMENT RAG
    # ========================================================

    if choice == "1":

        run_script(
            "ask_chunks_v3.py"
        )

        input(
            "\nPress Enter to return to FinLLM..."
        )


    # ========================================================
    # OPTION 2 — FINANCIAL QUERY
    # ========================================================

    elif choice == "2":

        run_script(
            "financial_query_cli.py"
        )

        input(
            "\nPress Enter to return to FinLLM..."
        )


    # ========================================================
    # OPTION 3 — COMPLIANCE REVIEW
    # ========================================================

    elif choice == "3":

        run_script(
            "case_compliance_explanation.py"
        )

        input(
            "\nPress Enter to return to FinLLM..."
        )


    # ========================================================
    # OPTION 4 — HUMAN CASE DECISION
    # ========================================================

    elif choice == "4":

        run_script(
            "case_decision_cli.py"
        )

        input(
            "\nPress Enter to return to FinLLM..."
        )


    # ========================================================
    # OPTION 5 — INVESTIGATION AGENT
    # ========================================================

    elif choice == "5":

        print(
            "\n=========================================="
        )

        print(
            "        FINLLM INVESTIGATION AGENT"
        )

        print(
            "=========================================="
        )

        run_script(
            "investigation_orchestrator.py"
        )

        input(
            "\nPress Enter to return to FinLLM..."
        )


    # ========================================================
    # OPTION 6 — FULL CASE PIPELINE
    # ========================================================

    elif choice == "6":

        print(
            "\n=========================================="
        )

        print(
            "          FINLLM CASE PIPELINE"
        )

        print(
            "=========================================="
        )

        print(
            "\nRunning automated case analysis up to "
            "the human-decision boundary."
        )

        print(
            "No human compliance decision will be "
            "automatically changed."
        )

        run_script(
            "case_pipeline_orchestrator.py"
        )

        input(
            "\nPress Enter to return to FinLLM..."
        )


    # ========================================================
    # OPTION 7 — EXIT
    # ========================================================

    elif choice == "7":

        print(
            "\nFinLLM session ended."
        )

        break


    # ========================================================
    # INVALID OPTION
    # ========================================================

    else:

        print(
            "\nInvalid option."
        )

        print(
            "Please enter a number from 1 to 7."
        )