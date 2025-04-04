import streamlit as st
import json
import collections

# ---------------- BST Implementation ---------------- #

class BSTNode:
    def __init__(self, medicine, quantity):
        self.medicine = medicine
        self.quantity = quantity
        self.left = None
        self.right = None

class BST:
    def __init__(self):
        self.root = None

    def insert(self, medicine, quantity):
        self.root = self._insert(self.root, medicine, quantity)

    def _insert(self, node, medicine, quantity):
        if not node:
            return BSTNode(medicine, quantity)
        if medicine < node.medicine:
            node.left = self._insert(node.left, medicine, quantity)
        elif medicine > node.medicine:
            node.right = self._insert(node.right, medicine, quantity)
        else:
            node.quantity = quantity  # update if already exists
        return node

    def search(self, prefix):
        results = []
        self._search(self.root, prefix.lower(), results)
        return results

    def _search(self, node, prefix, results):
        if node:
            if node.medicine.lower().startswith(prefix):
                results.append((node.medicine, node.quantity))
            self._search(node.left, prefix, results)
            self._search(node.right, prefix, results)

    def get_quantity(self, medicine):
        return self._get_quantity(self.root, medicine)

    def _get_quantity(self, node, medicine):
        if not node:
            return None
        if node.medicine == medicine:
            return node.quantity
        elif medicine < node.medicine:
            return self._get_quantity(node.left, medicine)
        else:
            return self._get_quantity(node.right, medicine)

# ---------------- Parsing Inventory ---------------- #

def parse_inventory(text):
    inventory = {}
    alternatives = {}

    for line in text.strip().splitlines():
        line = line.strip()
        if not line:
            continue
        if "[" in line:
            main, alt = line.split("[", 1)
            alt = alt.strip(" ]")
            alt_list = alt.split()
        else:
            main = line
            alt_list = []

        if ":" not in main:
            continue
        name, qty = main.strip().split(":")
        inventory[name.strip()] = int(qty.strip())
        if alt_list:
            alternatives[name.strip()] = alt_list

    return inventory, alternatives

# ---------------- Streamlit Interface ---------------- #

def main():
    st.title("PharmaFind")

    st.markdown(" Upload Inventory file (as per the given template)")
    st.markdown("---")
    template = """Paracetamol:0 [Crocin Dolo]
Crocin:0
Dolo:3
Ibuprofen:10
Cetirizine:4 [Levocetirizine Loratadine]
Levocetirizine:0
Loratadine:2
Aspirin:0 [Disprin]
Disprin:0
"""
    st.download_button(" Download Inventory Template", template, file_name="inventory_template.txt")
    uploaded_file = st.file_uploader("Upload `.txt` file", type="txt")

    if uploaded_file:
        contents = uploaded_file.read().decode("utf-8")
        inventory, alternatives = parse_inventory(contents)

        with open("inventory.json", "w") as f:
            json.dump({"inventory": inventory, "alternatives": alternatives}, f)

        st.success("Inventory updated successfully!")
    #added
    if st.button("Reset Inventory"):
        with open("inventory.json", "w") as f:
            json.dump({}, f)
        st.success("Inventory has been reset.")

    # Load inventory
    try:
        with open("inventory.json", "r") as f:
            data = json.load(f)
        inventory = data["inventory"]
        alternatives = data["alternatives"]
    except:
        inventory = {}
        alternatives = {}

    # Build BST
    bst = BST()
    for medicine, quantity in inventory.items():
        bst.insert(medicine, quantity)

    # Search functionality
    search_term = st.text_input("Search Medicine")
    if search_term:
        results = bst.search(search_term)
        if results:
            st.subheader("Search Results:")
            for medicine, qty in results:
                if qty > 0:
                    st.markdown(f"✅ **{medicine}**: {qty} in stock")
                else:
                    st.markdown(f"❌ **{medicine}**: Out of stock")
                    alts = alternatives.get(medicine, [])
                    alt_queue = collections.deque(alts) # Use a queue for alternatives
                    suggested = False
                    while alt_queue:
                        alt = alt_queue.popleft()
                        alt_qty = inventory.get(alt, 0)
                        if alt_qty > 0:
                            st.markdown(f"Try alternative: **{alt}** ({alt_qty} in stock)")
                            suggested = True
                            break
                    if not alts:
                        st.markdown(f" No alternatives listed for **{medicine}**.")
                    elif not suggested:
                        st.markdown(f"⚠️ Alternatives exist, but none are in stock.")
        else:
            st.warning("No medicine found!")

    # Download template


if __name__ == "__main__":
    main()
