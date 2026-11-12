import tkinter as tk
from tkinter import messagebox, Toplevel, StringVar

class Node:
    def __init__(self, key):
        self.key = key
        self.children = []  # Lista para soportar múltiples ramas (hijos)

        self.x = 0
        self.y = 0


class Tree:
    def __init__(self, root_key=50):
        self.root = Node(root_key) if root_key is not None else None

    def find_node_by_val(self, node, val):
        if not node:
            return None
        if node.key == val:
            return node
        for child in node.children:
            found = self.find_node_by_val(child, val)
            if found:
                return found
        return None

    def value_exists(self, node, val):
        if not node:
            return False
        if node.key == val:
            return True
        for child in node.children:
            if self.value_exists(child, val):
                return True
        return False

    def add_child(self, parent_node, new_val):
        if self.value_exists(self.root, new_val):
            return False, "El valor ya existe en el árbol. No se permiten duplicados."
        
        parent_node.children.append(Node(new_val))
        return True, "Hijo agregado con éxito."

    def delete_subtree(self, target_node):
        if target_node == self.root:
            return False, "No se puede eliminar la raíz principal directamente."
        success = self._remove_node_recursive(self.root, target_node)
        if success:
            return True, "Subárbol eliminado con éxito."
        return False, "No se pudo encontrar el nodo."

    def _remove_node_recursive(self, current, target):
        if current is None: 
            return False
        if target in current.children:
            current.children.remove(target)
            return True
        for child in current.children:
            if self._remove_node_recursive(child, target):
                return True
        return False

    def delete_node_only(self, target_node):
        if target_node == self.root and not target_node.children:
            return False, "No se puede eliminar la raíz única del árbol."
        
        # Si es hoja, simplemente lo removemos de los hijos de su padre
        if not target_node.children:
            if target_node == self.root:
                self.root = None
            else:
                self._remove_node_recursive(self.root, target_node)
            return True, "Nodo hoja eliminado con éxito."

        # Si tiene hijos, adoptamos a sus hijos como reemplazo
        parent, _ = self.find_parent_and_position(self.root, target_node)
        if target_node == self.root:
            new_root = self.root.children[0]
            new_root.children.extend(self.root.children[1:])
            self.root = new_root
            return True, "Raíz eliminada; el primer hijo asumió el control."
        
        idx = parent.children.index(target_node)
        parent.children[idx:idx+1] = target_node.children
        return True, "Nodo eliminado y sus ramas reorganizadas."

    # --- RECORRIDOS ---
    def get_preorder_nodes(self, node, res):
        if node:
            res.append(node)
            for child in node.children:
                self.get_preorder_nodes(child, res)

    def get_postorder_nodes(self, node, res):
        if node:
            for child in node.children:
                self.get_postorder_nodes(child, res)
            res.append(node)

    def get_inorder_nodes(self, node, res):
        if node:
            if node.children:
                self.get_inorder_nodes(node.children[0], res)
            res.append(node)
            for child in node.children[1:]:
                self.get_inorder_nodes(child, res)

    # --- ESTADÍSTICAS Y PROPIEDADES ---
    def get_height(self, node):
        if not node or not node.children:
            return 0
        return 1 + max(self.get_height(child) for child in node.children)

    def get_weight(self, node):
        if not node:
            return 0
        return 1 + sum(self.get_weight(child) for child in node.children)

    def get_max_children(self, node):
        """Calcula el número máximo de hijos que tiene cualquier nodo en el árbol"""
        if not node:
            return 0
        max_c = len(node.children)
        for child in node.children:
            max_c = max(max_c, self.get_max_children(child))
        return max_c

    def is_binary_structure(self, node):
        """Verifica recursivamente si ningún nodo supera los 2 hijos (estructura binaria)"""
        if not node:
            return True
        if len(node.children) > 2:
            return False
        return all(self.is_binary_structure(child) for child in node.children)

    def get_node_level(self, current, key, level):
        if not current:
            return -1
        if current.key == key:
            return level
        for child in current.children:
            l = self.get_node_level(child, key, level + 1)
            if l != -1: 
                return l
        return -1

    def find_parent_and_position(self, current, target):
        if not current:
            return None, -1
        if target in current.children:
            return current, current.children.index(target)
        for child in current.children:
            p, idx = self.find_parent_and_position(child, target)
            if p: 
                return p, idx
        return None, -1


# ==========================================
# 3. INTERFAZ GRÁFICA (Tkinter)
# ==========================================
class TreeApp:
    def __init__(self, root):
        self.window = root
        self.window.title("Visualizador de Árbol Multicamino / Binario")
        self.window.geometry("1100x750")
        self.window.config(bg="#f0f2f5")

        self.tree = Tree(50)
        self.zoom_factor = 1.0
        self.animation_id = None

        top_frame = tk.Frame(self.window, bg="#ffffff", bd=2, relief=tk.GROOVE)
        top_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=10)

        row1 = tk.Frame(top_frame, bg="#ffffff")
        row1.pack(fill=tk.X, padx=5, pady=5)

        tk.Button(row1, text="🌟 Cargar Ejemplo", bg="#009688", fg="white", font=("Arial", 9, "bold"), command=self.load_example_tree).pack(side=tk.LEFT, padx=3)
        tk.Button(row1, text="📊 Estadísticas del Árbol", bg="#3f51b5", fg="white", font=("Arial", 9, "bold"), command=self.show_tree_info).pack(side=tk.LEFT, padx=3)
        tk.Button(row1, text="🔍+ Zoom", bg="#607d8b", fg="white", font=("Arial", 9, "bold"), command=self.zoom_in).pack(side=tk.LEFT, padx=3)
        tk.Button(row1, text="🔍- Alejar", bg="#607d8b", fg="white", font=("Arial", 9, "bold"), command=self.zoom_out).pack(side=tk.LEFT, padx=3)

        tk.Label(row1, text="Buscar:", bg="#ffffff", font=("Arial", 9, "bold")).pack(side=tk.LEFT, padx=(15, 2))
        self.search_entry = tk.Entry(row1, width=8, font=("Arial", 10))
        self.search_entry.pack(side=tk.LEFT, padx=2)
        tk.Button(row1, text="🔍", bg="#ff5722", fg="white", font=("Arial", 9, "bold"), command=self.search_node_action).pack(side=tk.LEFT, padx=2)

        row2 = tk.Frame(top_frame, bg="#ffffff")
        row2.pack(fill=tk.X, padx=5, pady=5)

        tk.Button(row2, text="▶ Preorden", bg="#9c27b0", fg="white", font=("Arial", 9, "bold"), command=lambda: self.run_traversal("pre")).pack(side=tk.LEFT, padx=3)
        tk.Button(row2, text="▶ Inorden", bg="#ff9800", fg="white", font=("Arial", 9, "bold"), command=lambda: self.run_traversal("in")).pack(side=tk.LEFT, padx=3)
        tk.Button(row2, text="▶ Postorden", bg="#795548", fg="white", font=("Arial", 9, "bold"), command=lambda: self.run_traversal("post")).pack(side=tk.LEFT, padx=3)

        self.lbl_result = tk.Label(row2, text="Resultado: ", bg="#ffffff", font=("Arial", 10, "bold"))
        self.lbl_result.pack(side=tk.LEFT, padx=10)

        canvas_container = tk.Frame(self.window)
        canvas_container.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        self.canvas = tk.Canvas(canvas_container, bg="white", scrollregion=(0, 0, 4000, 2000))
        v_scrollbar = tk.Scrollbar(canvas_container, orient=tk.VERTICAL, command=self.canvas.yview)
        h_scrollbar = tk.Scrollbar(canvas_container, orient=tk.HORIZONTAL, command=self.canvas.xview)
        self.canvas.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)

        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.canvas.bind("<Button-1>", self.on_canvas_click)
        self.canvas.bind("<MouseWheel>", self._on_mouse_wheel)

        self.draw_tree()
        self.window.update_idletasks()
        self.canvas.xview_moveto(0.38)

    def center_window(self, dialog, width, height):
        self.window.update_idletasks()
        x = self.window.winfo_x() + (self.window.winfo_width() // 2) - (width // 2)
        y = self.window.winfo_y() + (self.window.winfo_height() // 2) - (height // 2)
        dialog.geometry(f"{width}x{height}+{x}+{y}")

    def zoom_in(self):
        if self.zoom_factor < 1.8:
            self.zoom_factor += 0.15
            self.draw_tree()

    def zoom_out(self):
        if self.zoom_factor > 0.5:
            self.zoom_factor -= 0.15
            self.draw_tree()

    def _on_mouse_wheel(self, event):
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def show_tree_info(self):
        height = self.tree.get_height(self.tree.root)
        weight = self.tree.get_weight(self.tree.root)
        max_children = self.tree.get_max_children(self.tree.root)
        
        # Detección automática del tipo de árbol basada en sus nodos actuales
        is_binary = self.tree.is_binary_structure(self.tree.root)
        tree_type = "Binario" if is_binary else "Multicamino / General"

        info_text = (
            f"🌲 TIPO DE ÁRBOL: {tree_type}\n\n"
            f"📏 MÉTRICAS:\n"
            f"• Altura: {height}\n"
            f"• Peso (Total de nodos): {weight}\n"
            f"• Número máximo de hijos en un nodo: {max_children}"
        )
        messagebox.showinfo("Estadísticas del Árbol", info_text)

    def search_node_action(self):
        try:
            val = int(self.search_entry.get())
        except ValueError:
            messagebox.showerror("Error", "Ingrese un número válido para buscar.")
            return

        target = self.tree.find_node_by_val(self.tree.root, val)
        if target:
            self.flash_node(target, 6)
        else:
            messagebox.showwarning("No encontrado", f"El valor {val} no existe en el árbol.")

    def flash_node(self, target_node, count):
        self.draw_tree(highlight_node=target_node, highlight_color="#FFEB3B" if count % 2 == 0 else "#FF9800")
        if count > 0:
            self.window.after(400, lambda: self.flash_node(target_node, count - 1))
        else:
            self.draw_tree()

    def on_canvas_click(self, event):
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)
        clicked_node = self.find_clicked_node(self.tree.root, x, y)
        if clicked_node:
            self.open_node_dialog(clicked_node)

    def find_clicked_node(self, node, x, y):
        if node is None:
            return None
        radius = int(20 * self.zoom_factor)
        dist_sq = (node.x - x)**2 + (node.y - y)**2
        if dist_sq <= radius**2:
            return node
        
        for child in node.children:
            found = self.find_clicked_node(child, x, y)
            if found:
                return found
        return None

    def open_node_dialog(self, node):
        level = self.tree.get_node_level(self.tree.root, node.key, 0)
        parent, _ = self.tree.find_parent_and_position(self.tree.root, node)
        
        if node == self.tree.root:
            node_type = "Raíz"
        elif not node.children:
            node_type = "Hoja"
        else:
            node_type = "Rama (Interno)"

        dialog = Toplevel(self.window)
        dialog.title(f"Nodo: {node.key}")
        self.center_window(dialog, 300, 260)
        dialog.config(bg="#f0f2f5")
        dialog.transient(self.window)
        dialog.grab_set()

        tk.Label(dialog, text=f"Información del Nodo [{node.key}]", bg="#f0f2f5", font=("Arial", 10, "bold")).pack(pady=8)
        
        info_str = (
            f"• Valor: {node.key}\n"
            f"• Nivel: {level}\n"
            f"• Tipo: {node_type}\n"
            f"• Total de hijos: {len(node.children)}"
        )
        tk.Label(dialog, text=info_str, bg="#ffffff", justify=tk.LEFT, relief=tk.GROOVE, padx=10, pady=5, font=("Arial", 9)).pack(pady=5, fill=tk.X, padx=15)

        def action_insert():
            dialog.destroy()
            self.handle_insert(node)

        def action_delete():
            dialog.destroy()
            self.handle_delete_choice(node)

        btn_frame = tk.Frame(dialog, bg="#f0f2f5")
        btn_frame.pack(pady=5)
        tk.Button(btn_frame, text="➕ Añadir Hijo", bg="#4CAF50", fg="white", font=("Arial", 9, "bold"), width=11, command=action_insert).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="🗑️ Eliminar", bg="#f44336", fg="white", font=("Arial", 9, "bold"), width=10, command=action_delete).pack(side=tk.LEFT, padx=5)

    def handle_insert(self, parent_node):
        dialog = Toplevel(self.window)
        dialog.title(f"Añadir hijo a {parent_node.key}")
        self.center_window(dialog, 280, 160)
        dialog.config(bg="#f0f2f5")
        dialog.transient(self.window)
        dialog.grab_set()

        tk.Label(dialog, text=f"Nuevo hijo para nodo: {parent_node.key}", bg="#f0f2f5", font=("Arial", 9, "bold")).pack(pady=10)
        val_entry = tk.Entry(dialog, width=12)
        val_entry.pack(pady=2)
        val_entry.focus_set()

        def confirm_insert():
            try:
                new_val = int(val_entry.get())
            except ValueError:
                messagebox.showerror("Error", "Ingrese un número entero válido.", parent=dialog)
                return

            success, msg = self.tree.add_child(parent_node, new_val)
            if not success:
                messagebox.showerror("Error", msg, parent=dialog)
                return

            dialog.destroy()
            self.draw_tree()

        tk.Button(dialog, text="Confirmar", bg="#2196F3", fg="white", font=("Arial", 9, "bold"), command=confirm_insert).pack(pady=10)

    def handle_delete_choice(self, target_node):
        del_dialog = Toplevel(self.window)
        del_dialog.title("Advertencia de Eliminación")
        self.center_window(del_dialog, 320, 200)
        del_dialog.config(bg="#fff3e0")
        del_dialog.transient(self.window)
        del_dialog.grab_set()

        tk.Label(del_dialog, text=f"⚠️ Advertencia: ¿Cómo deseas eliminar\nel nodo [{target_node.key}]?", bg="#fff3e0", fg="#d32f2f", font=("Arial", 10, "bold"), justify=tk.CENTER).pack(pady=10)

        def only_node():
            del_dialog.destroy()
            success, msg = self.tree.delete_node_only(target_node)
            if not success:
                messagebox.showwarning("Aviso", msg)
            else:
                self.draw_tree()

        def sub_tree():
            del_dialog.destroy()
            if target_node == self.tree.root:
                messagebox.showwarning("Aviso", "No se puede eliminar el subárbol de la raíz principal.")
                return
            success, msg = self.tree.delete_subtree(target_node)
            if not success:
                messagebox.showwarning("Aviso", msg)
            else:
                self.draw_tree()

        tk.Button(del_dialog, text="Eliminar Nodo (Reorganizar Hijos)", bg="#ff9800", fg="white", font=("Arial", 8, "bold"), width=34, command=only_node).pack(pady=4)
        tk.Button(del_dialog, text="Eliminar Todo el Subárbol", bg="#f44336", fg="white", font=("Arial", 8, "bold"), width=34, command=sub_tree).pack(pady=4)
        tk.Button(del_dialog, text="Cancelar", bg="#9e9e9e", fg="white", font=("Arial", 8, "bold"), width=34, command=del_dialog.destroy).pack(pady=4)

    def run_traversal(self, order_type):
        if self.animation_id:
            self.window.after_cancel(self.animation_id)

        nodes = []
        if order_type == "pre":
            self.tree.get_preorder_nodes(self.tree.root, nodes)
            name = "Preorden"
        elif order_type == "in":
            self.tree.get_inorder_nodes(self.tree.root, nodes)
            name = "Inorden (Aproximado)"
        elif order_type == "post":
            self.tree.get_postorder_nodes(self.tree.root, nodes)
            name = "Postorden"

        keys_str = ", ".join([str(n.key) for n in nodes])
        self.lbl_result.config(text=f"{name}: {keys_str}")
        self.animate_step(nodes, 0, [])

    def animate_step(self, nodes, index, visited_nodes):
        self.draw_tree()
        radius = int(20 * self.zoom_factor)
        for v_node in visited_nodes:
            self.canvas.create_oval(v_node.x - radius, v_node.y - radius, v_node.x + radius, v_node.y + radius, fill="#81c784", outline="#388e3c", width=2)
            self.canvas.create_text(v_node.x, v_node.y, text=str(v_node.key), fill="white", font=("Arial", int(10 * self.zoom_factor), "bold"))

        if index < len(nodes):
            current = nodes[index]
            self.canvas.create_oval(current.x - radius, current.y - radius, current.x + radius, current.y + radius, fill="#4CAF50", outline="#1b5e20", width=3)
            self.canvas.create_text(current.x, current.y, text=str(current.key), fill="white", font=("Arial", int(10 * self.zoom_factor), "bold"))
            visited_nodes.append(current)
            self.animation_id = self.window.after(600, lambda: self.animate_step(nodes, index + 1, visited_nodes))

    def load_example_tree(self):
        if self.animation_id: 
            self.window.after_cancel(self.animation_id)
        
        self.tree = Tree(50)
        node30 = Node(30)
        node40 = Node(40)
        node70 = Node(70)
        self.tree.root.children = [node30, node40, node70]
        
        node30.children = [Node(10), Node(25)]
        node70.children = [Node(60), Node(65), Node(80)]
        
        self.draw_tree()
        self.canvas.xview_moveto(0.38)
        self.lbl_result.config(text="Resultado: Ejemplo multicamino cargado.")

    def calculate_positions(self, node, x, y, total_width, v_spacing):
        if node is None: 
            return
        node.x = x
        node.y = y
        
        num_children = len(node.children)
        if num_children == 0:
            return

        start_x = x - (total_width / 2)
        step = total_width / max(1, num_children - 1) if num_children > 1 else 0

        for i, child in enumerate(node.children):
            child_x = start_x if num_children == 1 else start_x + (i * step)
            self.calculate_positions(child, child_x, y + v_spacing, total_width / max(2, num_children), v_spacing)

    def draw_nodes_lines(self, node, highlight_node=None, highlight_color=None):
        if node is None: 
            return
        radius = int(20 * self.zoom_factor)
        line_width = max(1, int(2 * self.zoom_factor))

        for child in node.children:
            self.canvas.create_line(node.x, node.y, child.x, child.y, width=line_width, fill="#888")
            self.draw_nodes_lines(child, highlight_node, highlight_color)

        fill_color = "#3f51b5"
        outline_color = "#1a237e"
        width = 2

        if node == highlight_node:
            fill_color = highlight_color
            outline_color = "#E65100"
            width = 4

        self.canvas.create_oval(node.x - radius, node.y - radius, node.x + radius, node.y + radius, fill=fill_color, outline=outline_color, width=width)
        self.canvas.create_text(node.x, node.y, text=str(node.key), fill="white", font=("Arial", int(10 * self.zoom_factor), "bold"))

    def draw_tree(self, highlight_node=None, highlight_color=None):
        self.canvas.delete("all")
        if self.tree.root:
            initial_width = int(800 * self.zoom_factor)
            v_spacing = int(70 * self.zoom_factor)
            self.calculate_positions(self.tree.root, 2000, 40, initial_width, v_spacing)
            self.draw_nodes_lines(self.tree.root, highlight_node, highlight_color)
            
            self.canvas.update_idletasks()
            self.canvas.config(scrollregion=(0, 0, 4000, 2000))

if __name__ == "__main__":
    root = tk.Tk()
    app = TreeApp(root)
    root.mainloop()