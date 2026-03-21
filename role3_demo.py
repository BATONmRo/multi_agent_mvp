from tools import tool_find_methods, check_reagents


def run_role3_demo(query: str) -> None:
    print("=" * 50)
    print("ROLE 3 DEMO: METHOD SEARCH")
    print("=" * 50)

    methods_result = tool_find_methods(query)
    print(methods_result)

    methods_found = methods_result.get("methods_found", [])
    if not methods_found:
        print("\nNo methods found")
        return

    best_method = methods_found[0]

    print("\n" + "=" * 50)
    print("ROLE 3 DEMO: REAGENT CHECK")
    print("=" * 50)

    reagents = best_method.get("reagents", [])
    reagents_result = check_reagents(reagents)
    print(reagents_result)

    print("\n" + "=" * 50)
    print("ROLE 3 DEMO: SUMMARY")
    print("=" * 50)
    print(f"Best method: {best_method.get('reaction')}")
    print(f"Conditions: {best_method.get('conditions')}")
    print(f"Yield: {best_method.get('yield')}")
    print(f"Issues: {reagents_result.get('issues')}")


if __name__ == "__main__":
    query = input("Enter reaction: ").strip()
    run_role3_demo(query)