from tkinter import Canvas, Tk
import time
import random

class Cell:
    def __init__(self, x1, y1, x2, y2, win=None):
        self.has_left_wall = True
        self.has_right_wall = True
        self.has_top_wall = True
        self.has_bottom_wall = True
        
        self._x1 = x1
        self._y1 = y1
        self._x2 = x2
        self._y2 = y2
        
        self._win = win
        self.visited = False

    def draw(self, x1=None, y1=None, x2=None, y2=None):
        if x1 is not None and y1 is not None and x2 is not None and y2 is not None:
            self._x1 = x1
            self._y1 = y1
            self._x2 = x2
            self._y2 = y2
        
        if self._win:
            bg_color = self._win.canvas.cget('background')
            
            if self.has_left_wall:
                self._win.canvas.create_line(self._x1, self._y1, self._x1, self._y2)
            else:
                self._win.canvas.create_line(self._x1, self._y1, self._x1, self._y2, fill=bg_color)
            
            if self.has_right_wall:
                self._win.canvas.create_line(self._x2, self._y1, self._x2, self._y2)
            else:
                self._win.canvas.create_line(self._x2, self._y1, self._x2, self._y2, fill=bg_color)
            
            if self.has_top_wall:
                self._win.canvas.create_line(self._x1, self._y1, self._x2, self._y1)
            else:
                self._win.canvas.create_line(self._x1, self._y1, self._x2, self._y1, fill=bg_color)
            
            if self.has_bottom_wall:
                self._win.canvas.create_line(self._x1, self._y2, self._x2, self._y2)
            else:
                self._win.canvas.create_line(self._x1, self._y2, self._x2, self._y2, fill=bg_color)

    def draw_move(self, to_cell, undo=False):
        if self._win:
            color = "red" if not undo else "gray"
            
            from_x = (self._x1 + self._x2) // 2  
            from_y = (self._y1 + self._y2) // 2
            
            to_x = (to_cell._x1 + to_cell._x2) // 2
            to_y = (to_cell._y1 + to_cell._y2) // 2
            
            self._win.canvas.create_line(from_x, from_y, to_x, to_y, fill=color)

class Maze:
    def __init__(self, x1, y1, num_rows, num_cols, cell_size_x, cell_size_y, win=None, seed=None):
        self.x1 = x1
        self.y1 = y1
        self.num_rows = num_rows
        self.num_cols = num_cols
        self.cell_size_x = cell_size_x
        self.cell_size_y = cell_size_y
        self.win = win

        if seed is not None:
            random.seed(seed)
        
        self._cells = []
        self._create_cells()
        self._break_entrance_and_exit()
        self._break_walls_r(0, 0)
        self._reset_cells_visited()

    def _create_cells(self):
        for col in range(self.num_cols):
            col_cells = []
            for row in range(self.num_rows):
                x1 = self.x1 + col * self.cell_size_x
                y1 = self.y1 + row * self.cell_size_y
                x2 = x1 + self.cell_size_x
                y2 = y1 + self.cell_size_y
                cell = Cell(x1, y1, x2, y2, self.win)
                col_cells.append(cell)
            self._cells.append(col_cells)
    
    def _draw_cell(self, i, j):
        x = self.x1 + j * self.cell_size_x
        y = self.y1 + i * self.cell_size_y
        cell = self._cells[j][i]
        cell.draw(x1=x, y1=y, x2=x + self.cell_size_x, y2=y + self.cell_size_y)
        self._animate()

    def _animate(self):
        if self.win:
            self.win.redraw()
            time.sleep(0.05)

    def draw(self):
        for col in range(self.num_cols):
            for row in range(self.num_rows):
                self._draw_cell(row, col)

    def draw_move(self, from_row, from_col, to_row, to_col, undo=False):
        from_cell = self._cells[from_col][from_row]
        to_cell = self._cells[to_col][to_row]
        from_cell.draw_move(to_cell, undo)

    def _break_entrance_and_exit(self):
        self._cells[0][0].has_top_wall = False
        self._cells[self.num_cols - 1][self.num_rows - 1].has_bottom_wall = False
        self._draw_cell(0, 0)
        self._draw_cell(self.num_rows - 1, self.num_cols - 1)

    def _break_walls_r(self, i, j):
        self._cells[j][i].visited = True
        directions = [(i - 1, j, 'top'), (i + 1, j, 'bottom'), (i, j - 1, 'left'), (i, j + 1, 'right')]

        random.shuffle(directions)

        for ni, nj, direction in directions:
            if 0 <= ni < self.num_rows and 0 <= nj < self.num_cols and not self._cells[nj][ni].visited:
                if direction == 'top':
                    self._cells[j][i].has_top_wall = False
                    self._cells[nj][ni].has_bottom_wall = False
                elif direction == 'bottom':
                    self._cells[j][i].has_bottom_wall = False
                    self._cells[nj][ni].has_top_wall = False
                elif direction == 'left':
                    self._cells[j][i].has_left_wall = False
                    self._cells[nj][ni].has_right_wall = False
                elif direction == 'right':  
                    self._cells[j][i].has_right_wall = False
                    self._cells[nj][ni].has_left_wall = False

                self._break_walls_r(ni, nj)
                self._draw_cell(i, j)


    def _reset_cells_visited(self):
        for col in self._cells:
            for cell in col:
                cell.visited = False

    def solve(self):
        return self._solve_r(0, 0)

    def _solve_r(self, i, j):
        self._animate()
        self._cells[j][i].visited = True

        if i == self.num_rows - 1 and j == self.num_cols - 1:
            return True

        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        for di, dj in directions:
            ni, nj = i + di, j + dj
            if 0 <= ni < self.num_rows and 0 <= nj < self.num_cols and not self._cells[nj][ni].visited:
                if (di == -1 and not self._cells[j][i].has_top_wall) or \
                   (di == 1 and not self._cells[j][i].has_bottom_wall) or \
                   (dj == -1 and not self._cells[j][i].has_left_wall) or \
                   (dj == 1 and not self._cells[j][i].has_right_wall):
                    self.draw_move(i, j, ni, nj)
                    if self._solve_r(ni, nj):
                        return True
                    self.draw_move(ni, nj, i, j, undo=True)
        
        return False

def main():
    win = Window(700,700)
    
    maze = Maze(50, 50, 10, 12, 50, 50, win)
    
    maze.draw()
    
    if maze.solve():
        print("Maze solved!")
    else:
        print("No solution found.")
    
    win.wait_for_close()

class Window:
    def __init__(self, width, height):
        self.width = width
        self.height = height

        self.root = Tk()
        self.root.title("Solve Mazer")

        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()

        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)

        self.root.geometry(f"{width}x{height}+{x}+{y}")

        self.root.protocol("WM_DELETE_WINDOW", self.close)

        self.canvas = Canvas(self.root, width=width, height=height)
        self.canvas.pack()

        self.is_running = False

    def redraw(self):
        self.root.update_idletasks()
        self.root.update()

    def wait_for_close(self):
        self.is_running = True
        while self.is_running:
            self.redraw()

    def close(self):
        self.is_running = False
        self.root.destroy()

if __name__ == "__main__":
    main()
