import pygame
import sys
import os
import math
import copy
from enum import Enum

# ---------------------- INIT ----------------------
import os
os.environ['SDL_VIDEO_CENTERED'] = '1' 

pygame.init()
pygame.display.set_caption("Cờ vua")
SCREEN_W, SCREEN_H = 1000, 800
screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))

clock = pygame.time.Clock()
FPS = 60

SIDE_PANEL_W = min(360, SCREEN_W // 5)
TOP_MARGIN = 100
BOTTOM_MARGIN = 80
AVAILABLE_W = SCREEN_W - (SIDE_PANEL_W + 80)
AVAILABLE_H = SCREEN_H - (TOP_MARGIN + BOTTOM_MARGIN)
SQUARE_SIZE = min(AVAILABLE_H // 8, AVAILABLE_W // 8)
BOARD_WIDTH = SQUARE_SIZE * 8
BOARD_HEIGHT = SQUARE_SIZE * 8
BOARD_X = (SCREEN_W - SIDE_PANEL_W - BOARD_WIDTH) // 2
BOARD_Y = TOP_MARGIN + (AVAILABLE_H - BOARD_HEIGHT) // 2


ICE_LIGHT = (240, 217, 181)  
ICE_DARK = (181, 136, 99)    
ACCENT = (200, 60, 60)       
GOLD = (242, 201, 76)
WHITE = (255, 255, 255)
BLACK = (20, 20, 30)        
SILVER = (120, 120, 140)
PANEL_BG = (25, 30, 40, 220)
VALID_MOVE_TINT = (100, 200, 100, 80)   
LAST_MOVE_TINT = (100, 150, 255, 80)    
HIGHLIGHT_TINT = (255, 255, 100, 80)    
SHADOW = (0, 0, 0, 60)

try:
    TITLE_FONT = pygame.font.SysFont("segoeui", 44, bold=True)
    HEADER_FONT = pygame.font.SysFont("segoeui", 22, bold=True)
    NORMAL_FONT = pygame.font.SysFont("segoeui", 18)
    XY_FONT = pygame.font.SysFont("segoeui", 30, bold=True)
except:
    TITLE_FONT = pygame.font.SysFont(None, 44, bold=True)
    HEADER_FONT = pygame.font.SysFont(None, 22, bold=True)
    NORMAL_FONT = pygame.font.SysFont(None, 18)
    XY_FONT = pygame.font.SysFont(None, 30, bold=True)

BOARD_SIZE = 8

ASSETS_DIR = os.path.join(os.path.dirname(__file__), "assets")

# ---------------------- ENUMS & PIECE CLASS ----------------------
class PieceType(Enum):
    PAWN = 1
    ROOK = 2
    KNIGHT = 3
    BISHOP = 4
    QUEEN = 5
    KING = 6

class PieceColor(Enum):
    WHITE = 1
    BLACK = 2

class Piece:
    piece_images = {}
    use_images = False

    def __init__(self, ptype: PieceType, color: PieceColor):
        self.piece_type = ptype
        self.color = color
        self.has_moved = False

    @staticmethod
    def try_load_images(square_size):
        """
        Attempt to load 12 images from assets. If any fail, set use_images=False.
        """
        Piece.piece_images = {}
        required = [
            ("white", "pawn"), ("white", "rook"), ("white", "knight"), ("white", "bishop"), ("white", "queen"), ("white", "king"),
            ("black", "pawn"), ("black", "rook"), ("black", "knight"), ("black", "bishop"), ("black", "queen"), ("black", "king"),
        ]
        ok = True
        target = square_size - 12
        
        print(f"Assets directory: {ASSETS_DIR}")
        print(f"Directory exists: {os.path.exists(ASSETS_DIR)}")
        
        if not os.path.exists(ASSETS_DIR):
            print("Assets directory not found! Using vector graphics.")
            ok = False
            Piece.use_images = False
            return

        for color_name, name in required:
            filename = f"{color_name}_{name}.png"
            path = os.path.join(ASSETS_DIR, filename)
            print(f"Looking for: {filename} at {path}")
            
            try:
                if not os.path.exists(path):
                    print(f"File not found: {filename}")
                    ok = False
                    break
                    
                img = pygame.image.load(path).convert_alpha()
                img = pygame.transform.smoothscale(img, (target, target))
                
                tint = pygame.Surface((target, target), pygame.SRCALPHA)
                img.blit(tint, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)
                
                Piece.piece_images[(color_name, name)] = img
                print(f"Successfully loaded: {filename}")
                
            except Exception as e:
                print(f"Error loading {filename}: {e}")
                ok = False
                break
        
        Piece.use_images = ok
        if ok:
            print("All piece images loaded successfully!")
        else:
            print("Using vector graphics instead of images.")
            Piece.piece_images = {}

    def draw(self, surf, x, y):

        is_white = (self.color == PieceColor.WHITE)
        size = SQUARE_SIZE - 12
        
        if Piece.use_images:
            key = ("white" if is_white else "black", self.piece_type.name.lower())
            img = Piece.piece_images.get(key)
            if img:
                surf.blit(img, (x + (SQUARE_SIZE - size)//2, y + (SQUARE_SIZE - size)//2))
                return
        

        cx = x + SQUARE_SIZE // 2
        cy = y + SQUARE_SIZE // 2
        base_r = int(size * 0.42)  
        
        if is_white:
            piece_color = (250, 250, 255)  
            border_color = (180, 200, 220)  
            shadow_color = (200, 210, 220)  
        else:
            piece_color = (30, 30, 40)    
            border_color = (80, 100, 120)  
            shadow_color = (60, 70, 80)    
        

        pygame.draw.circle(surf, shadow_color, (cx+2, cy+2), base_r)
        pygame.draw.circle(surf, piece_color, (cx, cy), base_r)
        pygame.draw.circle(surf, border_color, (cx, cy), base_r, 2)
        

        if self.piece_type == PieceType.PAWN:
            head_r = int(base_r * 0.5)
            pygame.draw.circle(surf, border_color, (cx, cy - int(base_r*0.2)), head_r)
            pygame.draw.circle(surf, border_color, (cx, cy - int(base_r*0.2)), head_r, 1)
            pygame.draw.ellipse(surf, border_color, (cx - int(base_r*0.7), cy + int(base_r*0.3), int(base_r*1.4), int(base_r*0.4)))
            
        elif self.piece_type == PieceType.ROOK:
            body_rect = pygame.Rect(cx - int(base_r*0.6), cy - int(base_r*0.5), int(base_r*1.2), int(base_r*1.0))
            pygame.draw.rect(surf, border_color, body_rect, border_radius=4)
            for i in range(3):
                bx = cx - int(base_r*0.5) + i * int(base_r*0.5)
                battlement = pygame.Rect(bx, cy - int(base_r*0.7), int(base_r*0.3), int(base_r*0.2))
                pygame.draw.rect(surf, border_color, battlement)
                
        elif self.piece_type == PieceType.KNIGHT:
            points = [
                (cx - int(base_r*0.3), cy + int(base_r*0.4)),
                (cx - int(base_r*0.8), cy + int(base_r*0.2)),
                (cx - int(base_r*0.6), cy - int(base_r*0.3)),
                (cx, cy - int(base_r*0.5)),
                (cx + int(base_r*0.4), cy - int(base_r*0.2)),
                (cx + int(base_r*0.3), cy + int(base_r*0.4)),
                (cx - int(base_r*0.3), cy + int(base_r*0.4))
            ]
            pygame.draw.polygon(surf, border_color, points)
            pygame.draw.line(surf, border_color, (cx - int(base_r*0.2), cy - int(base_r*0.4)), 
                            (cx - int(base_r*0.4), cy - int(base_r*0.6)), 2)
            
        elif self.piece_type == PieceType.BISHOP:
            pygame.draw.circle(surf, border_color, (cx, cy), base_r)
            hat_points = [
                (cx, cy - int(base_r*0.8)),
                (cx - int(base_r*0.4), cy - int(base_r*0.2)),
                (cx + int(base_r*0.4), cy - int(base_r*0.2))
            ]
            pygame.draw.polygon(surf, border_color, hat_points)
            pygame.draw.line(surf, piece_color, cx, cy - int(base_r*0.3), cx, cy + int(base_r*0.1), 2)
            pygame.draw.line(surf, piece_color, cx - int(base_r*0.15), cy - int(base_r*0.1), cx + int(base_r*0.15), cy - int(base_r*0.1), 2)
            
        elif self.piece_type == PieceType.QUEEN:
            pygame.draw.circle(surf, border_color, (cx, cy), base_r)
            for i in range(5):
                angle = 2 * math.pi * i / 5 - math.pi/2
                inner_x = cx + math.cos(angle) * base_r * 0.6
                inner_y = cy + math.sin(angle) * base_r * 0.6
                outer_x = cx + math.cos(angle) * base_r * 0.9
                outer_y = cy + math.sin(angle) * base_r * 0.9
                pygame.draw.line(surf, border_color, (inner_x, inner_y), (outer_x, outer_y), 3)
            pygame.draw.circle(surf, (255, 215, 0) if is_white else (200, 150, 0), (cx, cy - int(base_r*0.3)), int(base_r*0.15))
            
        elif self.piece_type == PieceType.KING:
            pygame.draw.circle(surf, border_color, (cx, cy), base_r)
            crown_points = [
                (cx - int(base_r*0.6), cy - int(base_r*0.3)),
                (cx - int(base_r*0.3), cy - int(base_r*0.6)),
                (cx, cy - int(base_r*0.8)),
                (cx + int(base_r*0.3), cy - int(base_r*0.6)),
                (cx + int(base_r*0.6), cy - int(base_r*0.3))
            ]
            pygame.draw.lines(surf, border_color, False, crown_points, 3)
            pygame.draw.line(surf, border_color, (cx, cy - int(base_r*0.8)), (cx, cy - int(base_r*0.4)), 3)
            pygame.draw.line(surf, border_color, (cx - int(base_r*0.15), cy - int(base_r*0.6)), (cx + int(base_r*0.15), cy - int(base_r*0.6)), 3)

# ---------------------- BOARD / GAME LOGIC ----------------------
class Board:
    def __init__(self):
        self.board = [[None]*BOARD_SIZE for _ in range(BOARD_SIZE)]
        self.selected_piece = None
        self.valid_moves = []
        self.turn = PieceColor.WHITE
        self.game_over = False
        self.winner = None
        self.move_history = []
        self.last_move = None
        self.ai_thinking = False
        self.setup_board()

    def setup_board(self):
        # pawns
        for c in range(8):
            self.board[1][c] = Piece(PieceType.PAWN, PieceColor.BLACK)
            self.board[6][c] = Piece(PieceType.PAWN, PieceColor.WHITE)
        # rooks
        self.board[0][0] = Piece(PieceType.ROOK, PieceColor.BLACK)
        self.board[0][7] = Piece(PieceType.ROOK, PieceColor.BLACK)
        self.board[7][0] = Piece(PieceType.ROOK, PieceColor.WHITE)
        self.board[7][7] = Piece(PieceType.ROOK, PieceColor.WHITE)
        # knights
        self.board[0][1] = Piece(PieceType.KNIGHT, PieceColor.BLACK)
        self.board[0][6] = Piece(PieceType.KNIGHT, PieceColor.BLACK)
        self.board[7][1] = Piece(PieceType.KNIGHT, PieceColor.WHITE)
        self.board[7][6] = Piece(PieceType.KNIGHT, PieceColor.WHITE)
        # bishops
        self.board[0][2] = Piece(PieceType.BISHOP, PieceColor.BLACK)
        self.board[0][5] = Piece(PieceType.BISHOP, PieceColor.BLACK)
        self.board[7][2] = Piece(PieceType.BISHOP, PieceColor.WHITE)
        self.board[7][5] = Piece(PieceType.BISHOP, PieceColor.WHITE)
        # queens
        self.board[0][3] = Piece(PieceType.QUEEN, PieceColor.BLACK)
        self.board[7][3] = Piece(PieceType.QUEEN, PieceColor.WHITE)
        # kings
        self.board[0][4] = Piece(PieceType.KING, PieceColor.BLACK)
        self.board[7][4] = Piece(PieceType.KING, PieceColor.WHITE)

    def in_bounds(self, r, c):
        return 0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE

    def get_valid_moves(self, row, col):
        p = self.board[row][col]
        if not p: return []
        moves = []
        if p.piece_type == PieceType.PAWN:
            dirr = 1 if p.color == PieceColor.BLACK else -1
            start = 1 if p.color == PieceColor.BLACK else 6
            if self.in_bounds(row+dirr, col) and not self.board[row+dirr][col]:
                moves.append((row+dirr, col))
                if row == start and self.in_bounds(row+2*dirr, col) and not self.board[row+2*dirr][col]:
                    moves.append((row+2*dirr, col))
            for dc in (-1,1):
                nr, nc = row+dirr, col+dc
                if self.in_bounds(nr, nc) and self.board[nr][nc] and self.board[nr][nc].color != p.color:
                    moves.append((nr, nc))
        elif p.piece_type == PieceType.ROOK:
            dirs = [(1,0),(-1,0),(0,1),(0,-1)]
            for dr,dc in dirs:
                for i in range(1,8):
                    r,c = row+dr*i, col+dc*i
                    if not self.in_bounds(r,c): break
                    if not self.board[r][c]:
                        moves.append((r,c))
                    else:
                        if self.board[r][c].color != p.color:
                            moves.append((r,c))
                        break
        elif p.piece_type == PieceType.BISHOP:
            dirs = [(1,1),(1,-1),(-1,1),(-1,-1)]
            for dr,dc in dirs:
                for i in range(1,8):
                    r,c = row+dr*i, col+dc*i
                    if not self.in_bounds(r,c): break
                    if not self.board[r][c]:
                        moves.append((r,c))
                    else:
                        if self.board[r][c].color != p.color:
                            moves.append((r,c))
                        break
        elif p.piece_type == PieceType.QUEEN:
            dirs = [(1,0),(-1,0),(0,1),(0,-1),(1,1),(1,-1),(-1,1),(-1,-1)]
            for dr,dc in dirs:
                for i in range(1,8):
                    r,c = row+dr*i, col+dc*i
                    if not self.in_bounds(r,c): break
                    if not self.board[r][c]:
                        moves.append((r,c))
                    else:
                        if self.board[r][c].color != p.color:
                            moves.append((r,c))
                        break
        elif p.piece_type == PieceType.KNIGHT:
            deltas = [(2,1),(2,-1),(-2,1),(-2,-1),(1,2),(1,-2),(-1,2),(-1,-2)]
            for dr,dc in deltas:
                r,c = row+dr, col+dc
                if self.in_bounds(r,c) and (not self.board[r][c] or self.board[r][c].color != p.color):
                    moves.append((r,c))
        elif p.piece_type == PieceType.KING:
            for dr in (-1,0,1):
                for dc in (-1,0,1):
                    if dr==0 and dc==0: continue
                    r,c = row+dr, col+dc
                    if self.in_bounds(r,c) and (not self.board[r][c] or self.board[r][c].color != p.color):
                        moves.append((r,c))
        return moves

    def select_by_mouse(self, mx, my):
        if self.game_over: return
        col = (mx - BOARD_X) // SQUARE_SIZE
        row = (my - BOARD_Y) // SQUARE_SIZE
        if not self.in_bounds(row, col): return
        p = self.board[row][col]
        if self.selected_piece:
            if (row, col) in self.valid_moves:
                fr, fc = self.selected_piece
                self.last_move = ((fr, fc), (row, col))
                self.move_history.append(self.last_move)
                self.animate_and_apply(fr, fc, row, col)
                self.selected_piece = None
                self.valid_moves = []
                self.turn = PieceColor.BLACK if self.turn == PieceColor.WHITE else PieceColor.WHITE
                self.check_game_over()
            elif p and p.color == self.turn:
                self.selected_piece = (row, col)
                self.valid_moves = self.get_valid_moves(row, col)
            else:
                self.selected_piece = None
                self.valid_moves = []
        else:
            if p and p.color == self.turn:
                self.selected_piece = (row, col)
                self.valid_moves = self.get_valid_moves(row, col)

    def animate_and_apply(self, fr, fc, tr, tc):
        piece = self.board[fr][fc]
        if not piece:
            self.move_piece(fr, fc, tr, tc)
            return
        start_x = BOARD_X + fc * SQUARE_SIZE
        start_y = BOARD_Y + fr * SQUARE_SIZE
        end_x = BOARD_X + tc * SQUARE_SIZE
        end_y = BOARD_Y + tr * SQUARE_SIZE
        steps = 14
        for step in range(steps + 1):
            t = step / steps
            curx = start_x + (end_x - start_x) * t
            cury = start_y + (end_y - start_y) * t
            draw_background()
            draw_title_panel()
            draw_board(self)
            piece.draw(screen, int(curx) + 5, int(cury) + 5)
            pygame.display.flip()
            clock.tick(FPS)
        self.move_piece(fr, fc, tr, tc)

    def move_piece(self, fr, fc, tr, tc):
        p = self.board[fr][fc]
        self.board[tr][tc] = p
        self.board[fr][fc] = None
        if p:
            p.has_moved = True

    def check_game_over(self):
        wking = False
        bking = False
        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                p = self.board[r][c]
                if p and p.piece_type == PieceType.KING:
                    if p.color == PieceColor.WHITE: wking = True
                    else: bking = True
        if not wking:
            self.game_over = True
            self.winner = PieceColor.BLACK
        elif not bking:
            self.game_over = True
            self.winner = PieceColor.WHITE

# ---------------------- AI (Minimax + Alpha-Beta) ----------------------
class ChessAI:
    def __init__(self, color=PieceColor.BLACK, depth=3):
        self.color = color
        self.depth = depth
        self.piece_values = {
            PieceType.PAWN: 100,
            PieceType.KNIGHT: 320,
            PieceType.BISHOP: 330,
            PieceType.ROOK: 500,
            PieceType.QUEEN: 900,
            PieceType.KING: 20000
        }
        self.pawn_table = [
            [0,0,0,0,0,0,0,0],
            [50,50,50,50,50,50,50,50],
            [10,10,20,30,30,20,10,10],
            [5,5,10,25,25,10,5,5],
            [0,0,0,20,20,0,0,0],
            [5,-5,-10,0,0,-10,-5,5],
            [5,10,10,-20,-20,10,10,5],
            [0,0,0,0,0,0,0,0]
        ]
        self.knight_table = [[-40,-30,-20,-20,-20,-20,-30,-40],
                              [-30,-10,10,5,5,10,-10,-30],
                              [-30,5,15,10,10,15,5,-30],
                              [-30,5,15,10,10,15,5,-30],
                              [-30,0,10,15,15,10,0,-30],
                              [-35,-5,0,5,5,0,-5,-35],
                              [-40,-20,-10,0,0,-10,-20,-40],
                              [-50,-40,-30,-30,-30,-30,-40,-50]]
        self.bishop_table = [[-20,-10,-10,-10,-10,-10,-10,-20],
                             [-10,5,0,0,0,0,5,-10],
                             [-10,10,10,15,15,10,10,-10],
                             [-10,0,15,20,20,15,0,-10],
                             [-10,5,10,18,18,10,5,-10],
                             [-10,0,10,15,15,10,0,-10],
                             [-10,0,0,0,0,0,0,-10],
                             [-20,-10,-10,-10,-10,-10,-10,-20]]
        self.rook_table = [[0,0,5,10,10,5,0,0],
                           [0,0,5,10,10,5,0,0],
                           [0,0,5,10,10,5,0,0],
                           [0,0,5,10,10,5,0,0],
                           [0,0,5,10,10,5,0,0],
                           [0,0,5,10,10,5,0,0],
                           [25,25,25,25,25,25,25,25],
                           [0,0,5,10,10,5,0,0]]
        self.king_table = [[-30,-40,-40,-50,-50,-40,-40,-30],
                           [-30,-40,-40,-50,-50,-40,-40,-30],
                           [-30,-40,-40,-50,-50,-40,-40,-30],
                           [-30,-40,-40,-50,-50,-40,-40,-30],
                           [-20,-30,-30,-40,-40,-30,-30,-20],
                           [-10,-20,-20,-20,-20,-20,-20,-10],
                           [20,20,0,0,0,0,20,20],
                           [20,30,10,0,0,10,30,20]]

    def evaluate_board(self, board_obj: Board):
        total = 0
        for r in range(8):
            for c in range(8):
                p = board_obj.board[r][c]
                if not p: continue
                val = self.piece_values[p.piece_type]
                pos = 0
                if p.piece_type == PieceType.PAWN:
                    t = self.pawn_table if p.color == PieceColor.WHITE else list(reversed(self.pawn_table))
                    pos = t[r][c]
                elif p.piece_type == PieceType.KNIGHT:
                    t = self.knight_table if p.color == PieceColor.WHITE else list(reversed(self.knight_table))
                    pos = t[r][c]
                elif p.piece_type == PieceType.BISHOP:
                    t = self.bishop_table if p.color == PieceColor.WHITE else list(reversed(self.bishop_table))
                    pos = t[r][c]
                elif p.piece_type == PieceType.ROOK:
                    t = self.rook_table if p.color == PieceColor.WHITE else list(reversed(self.rook_table))
                    pos = t[r][c]
                elif p.piece_type == PieceType.KING:
                    t = self.king_table if p.color == PieceColor.WHITE else list(reversed(self.king_table))
                    pos = t[r][c]
                piece_score = val + pos
                if p.color == self.color:
                    total += piece_score
                else:
                    total -= piece_score
        return total

    def copy_board_state(self, board_obj: Board):
        new = [[None]*8 for _ in range(8)]
        for r in range(8):
            for c in range(8):
                p = board_obj.board[r][c]
                if p:
                    np = Piece(p.piece_type, p.color)
                    np.has_moved = p.has_moved
                    new[r][c] = np
        return new

    def make_move(self, state, from_pos, to_pos):
        fr, fc = from_pos
        tr, tc = to_pos
        p = state[fr][fc]
        state[tr][tc] = p
        state[fr][fc] = None
        if p:
            p.has_moved = True

    def moves_for_piece(self, state, row, col):
        p = state[row][col]
        if not p: return []
        moves = []
        if p.piece_type == PieceType.PAWN:
            dirr = 1 if p.color == PieceColor.BLACK else -1
            start = 1 if p.color == PieceColor.BLACK else 6
            if 0 <= row+dirr < 8 and not state[row+dirr][col]:
                moves.append((row+dirr, col))
                if row == start and not state[row+2*dirr][col]:
                    moves.append((row+2*dirr, col))
            for dc in (-1,1):
                nr, nc = row+dirr, col+dc
                if 0 <= nr < 8 and 0 <= nc < 8 and state[nr][nc] and state[nr][nc].color != p.color:
                    moves.append((nr,nc))
        elif p.piece_type == PieceType.ROOK:
            dirs = [(1,0),(-1,0),(0,1),(0,-1)]
            for dr,dc in dirs:
                for i in range(1,8):
                    r,c = row+dr*i, col+dc*i
                    if not (0<=r<8 and 0<=c<8): break
                    if not state[r][c]: moves.append((r,c))
                    else:
                        if state[r][c].color != p.color: moves.append((r,c))
                        break
        elif p.piece_type == PieceType.BISHOP:
            dirs = [(1,1),(1,-1),(-1,1),(-1,-1)]
            for dr,dc in dirs:
                for i in range(1,8):
                    r,c = row+dr*i, col+dc*i
                    if not (0<=r<8 and 0<=c<8): break
                    if not state[r][c]: moves.append((r,c))
                    else:
                        if state[r][c].color != p.color: moves.append((r,c))
                        break
        elif p.piece_type == PieceType.QUEEN:
            dirs = [(1,0),(-1,0),(0,1),(0,-1),(1,1),(1,-1),(-1,1),(-1,-1)]
            for dr,dc in dirs:
                for i in range(1,8):
                    r,c = row+dr*i, col+dc*i
                    if not (0<=r<8 and 0<=c<8): break
                    if not state[r][c]: moves.append((r,c))
                    else:
                        if state[r][c].color != p.color: moves.append((r,c))
                        break
        elif p.piece_type == PieceType.KNIGHT:
            deltas = [(2,1),(2,-1),(-2,1),(-2,-1),(1,2),(1,-2),(-1,2),(-1,-2)]
            for dr,dc in deltas:
                r,c = row+dr, col+dc
                if 0<=r<8 and 0<=c<8 and (not state[r][c] or state[r][c].color != p.color):
                    moves.append((r,c))
        elif p.piece_type == PieceType.KING:
            for dr in (-1,0,1):
                for dc in (-1,0,1):
                    if dr==0 and dc==0: continue
                    r,c = row+dr, col+dc
                    if 0<=r<8 and 0<=c<8 and (not state[r][c] or state[r][c].color != p.color):
                        moves.append((r,c))
        return moves

    def all_moves(self, state, color):
        moves = []
        for r in range(8):
            for c in range(8):
                p = state[r][c]
                if p and p.color == color:
                    for mv in self.moves_for_piece(state, r, c):
                        moves.append(((r,c), mv))
        return moves

    def minimax(self, state, depth, alpha, beta, maximizing_color):
        if depth == 0:
            class TempBoard:
                def __init__(self, state):
                    self.board = state
            temp_board = TempBoard(state)
            return self.evaluate_board(temp_board), None
        if maximizing_color == self.color:
            max_eval = -float('inf')
            best = None
            moves = self.all_moves(state, maximizing_color)
            if not moves:
                return self.evaluate_board(BoardWrapper(state)), None
            for mv in moves:
                from_pos, to_pos = mv
                new_state = copy.deepcopy(state)
                self.make_move(new_state, from_pos, to_pos)
                eval_val, _ = self.minimax(new_state, depth-1, alpha, beta, PieceColor.BLACK if maximizing_color==PieceColor.WHITE else PieceColor.WHITE)
                if eval_val > max_eval:
                    max_eval = eval_val
                    best = mv
                alpha = max(alpha, eval_val)
                if beta <= alpha:
                    break
            return max_eval, best
        else:
            min_eval = float('inf')
            best = None
            moves = self.all_moves(state, maximizing_color)
            if not moves:
                return self.evaluate_board(BoardWrapper(state)), None
            for mv in moves:
                from_pos, to_pos = mv
                new_state = copy.deepcopy(state)
                self.make_move(new_state, from_pos, to_pos)
                eval_val, _ = self.minimax(new_state, depth-1, alpha, beta, PieceColor.BLACK if maximizing_color==PieceColor.WHITE else PieceColor.WHITE)
                if eval_val < min_eval:
                    min_eval = eval_val
                    best = mv
                beta = min(beta, eval_val)
                if beta <= alpha:
                    break
            return min_eval, best

    def get_best_move(self, board_obj: Board):
        state = self.copy_board_state(board_obj)
        _, best = self.minimax(state, self.depth, -float('inf'), float('inf'), self.color)
        return best

class BoardWrapper:
    def __init__(self, state):
        self.board = state
        self.turn = PieceColor.WHITE  
        self.game_over = False
        self.winner = None
        self.move_history = []
        self.last_move = None
        self.ai_thinking = False
        self.selected_piece = None
        self.valid_moves = []

# ---------------------- DRAW UI ----------------------
def draw_background():
    screen.fill((40, 60, 80))
    glow = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
    pygame.draw.circle(glow, (220, 245, 255, 30), (SCREEN_W//2, TOP_MARGIN//2), SCREEN_W//4)
    screen.blit(glow, (0,0))

def draw_title_panel():
    title = TITLE_FONT.render("Cờ vua", True, WHITE)
    screen.blit(title, (340, 22))
    px = SCREEN_W - SIDE_PANEL_W - 30
    py = 80
    panel_rect = pygame.Rect(px, py, SIDE_PANEL_W, SCREEN_H - py - 40)
    shadow = pygame.Surface((panel_rect.width, panel_rect.height), pygame.SRCALPHA)
    shadow.fill((0,0,0,120))
    screen.blit(shadow, (panel_rect.x+8, panel_rect.y+8))
    panel = pygame.Surface((panel_rect.width, panel_rect.height), pygame.SRCALPHA)
    panel.fill((20, 28, 36, 220))
    screen.blit(panel, (panel_rect.x, panel_rect.y))
    pygame.draw.rect(screen, SILVER, panel_rect, 2, border_radius=10)
    header = HEADER_FONT.render("THÔNG TIN", True, ACCENT)
    screen.blit(header, (panel_rect.x + 16, panel_rect.y + 14))
    return panel_rect

def draw_board(board_obj: Board):
    frame = pygame.Rect(BOARD_X-12, BOARD_Y-12, BOARD_WIDTH+24, BOARD_HEIGHT+24)
    sh = pygame.Surface((frame.width, frame.height), pygame.SRCALPHA)
    sh.fill(SHADOW)
    screen.blit(sh, (frame.x+4, frame.y+4)) 
    pygame.draw.rect(screen, (220, 240, 250), frame, border_radius=12)
    pygame.draw.rect(screen, (160, 200, 220), frame, 4, border_radius=12) 
    
    for r in range(8):
        for c in range(8):
            x = BOARD_X + c*SQUARE_SIZE
            y = BOARD_Y + r*SQUARE_SIZE
            is_light = ((r + c) % 2 == 0)
            color = ICE_LIGHT if is_light else ICE_DARK
            pygame.draw.rect(screen, color, (x, y, SQUARE_SIZE, SQUARE_SIZE))

    if board_obj.last_move:
        (fr,fc),(tr,tc) = board_obj.last_move
        for (r,c) in [(fr,fc),(tr,tc)]:
            s = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE), pygame.SRCALPHA)
            s.fill(LAST_MOVE_TINT)
            screen.blit(s, (BOARD_X + c*SQUARE_SIZE, BOARD_Y + r*SQUARE_SIZE))

    pulse = (pygame.time.get_ticks() // 200) % 10
    for (r,c) in board_obj.valid_moves:
        x = BOARD_X + c*SQUARE_SIZE
        y = BOARD_Y + r*SQUARE_SIZE
        alpha = 80 + int(40 * math.sin(pulse * 0.3)) 
        s = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE), pygame.SRCALPHA)
        s.fill((VALID_MOVE_TINT[0], VALID_MOVE_TINT[1], VALID_MOVE_TINT[2], alpha))
        screen.blit(s, (x, y))
        dot = (x + SQUARE_SIZE//2, y + SQUARE_SIZE//2)
        dot_r = SQUARE_SIZE//14  
        pygame.draw.circle(screen, (60,100,120), dot, dot_r)

    if board_obj.selected_piece:
        r,c = board_obj.selected_piece
        x = BOARD_X + c*SQUARE_SIZE
        y = BOARD_Y + r*SQUARE_SIZE
        s = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE), pygame.SRCALPHA)
        alpha = 80 + int(40 * math.sin((pygame.time.get_ticks()//150) * 0.2))  
        s.fill((HIGHLIGHT_TINT[0], HIGHLIGHT_TINT[1], HIGHLIGHT_TINT[2], alpha))
        screen.blit(s, (x, y))
        pygame.draw.rect(screen, ACCENT, (x, y, SQUARE_SIZE, SQUARE_SIZE), 2)  

    for r in range(8):
        for c in range(8):
            p = board_obj.board[r][c]
            if p:
                x = BOARD_X + c*SQUARE_SIZE
                y = BOARD_Y + r*SQUARE_SIZE
                p.draw(screen, x+5, y+5)

    for i in range(8):
        ch = chr(97 + i)
        tx = XY_FONT.render(ch, True, (100, 130, 160)) 
        screen.blit(tx, (BOARD_X + i*SQUARE_SIZE + SQUARE_SIZE//2 - tx.get_width()//2, BOARD_Y + BOARD_HEIGHT + 15))
        num = XY_FONT.render(str(8 - i), True, (100, 130, 160))
        screen.blit(num, (BOARD_X - 40, BOARD_Y + i*SQUARE_SIZE + SQUARE_SIZE//2 - num.get_height()//2))

def draw_info(board_obj: Board, ai_obj: ChessAI, spinner_angle):
    px = SCREEN_W - SIDE_PANEL_W - 30
    py = 20
    turn_text = "Lượt: Trắng" if board_obj.turn == PieceColor.WHITE else "Lượt: Đen "
    tcol = WHITE if board_obj.turn == PieceColor.WHITE else (255,200,200)
    screen.blit(HEADER_FONT.render(turn_text, True, tcol), (px + 16, py + 110))
    screen.blit(NORMAL_FONT.render(f"Moves: {len(board_obj.move_history)}", True, WHITE), (px + 16, py + 180))
    
    if board_obj.ai_thinking:
        cx = px + SIDE_PANEL_W - 180
        cy = py + 160
        radius = 10
        pygame.draw.circle(screen, (20,28,36), (cx, cy), radius)
        start_ang = math.radians(spinner_angle)
        end_ang = start_ang + math.radians(240)
        steps = 28
        for i in range(steps):
            a1 = start_ang + (end_ang - start_ang) * i / steps
            a2 = start_ang + (end_ang - start_ang) * (i+1) / steps
            x1 = cx + int(math.cos(a1)*radius)
            y1 = cy + int(math.sin(a1)*radius)
            x2 = cx + int(math.cos(a2)*radius)
            y2 = cy + int(math.sin(a2)*radius)
            col = (220,240,255) if i > steps*0.6 else (140,170,190)
            pygame.draw.line(screen, col, (x1,y1), (x2,y2), 4)
        screen.blit(NORMAL_FONT.render("Máy đang suy nghỉ", True, ACCENT), (px + 40, py + 150))
    
    if board_obj.game_over:
        overlay = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
        overlay.fill((0,0,0,160))
        screen.blit(overlay, (0,0))
        res = "Trắng thắng!" if board_obj.winner == PieceColor.WHITE else "Đen thắng! "
        txt = HEADER_FONT.render(res, True, GOLD)
        screen.blit(txt, (SCREEN_W//2 - txt.get_width()//2, SCREEN_H//2 - 40))
        sub = NORMAL_FONT.render("Nhấn R để bắt đầu lại hoặc ESC để thoát", True, WHITE)
        screen.blit(sub, (SCREEN_W//2 - sub.get_width()//2, SCREEN_H//2 + 12))

# ---------------------- MAIN LOOP ----------------------
def main(): 
    Piece.try_load_images(SQUARE_SIZE)
    print(f"Using images: {Piece.use_images}")
    board = Board()
    ai = ChessAI(PieceColor.BLACK, depth=3)
    running = True
    spinner_angle = 0
    vs_ai = True  

    while running:
        clock.tick(FPS)
        mx, my = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                if event.key == pygame.K_r:
                    board = Board()
                if event.key == pygame.K_m:  #
                    vs_ai = not vs_ai
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if BOARD_X <= mx <= BOARD_X + BOARD_WIDTH and BOARD_Y <= my <= BOARD_Y + BOARD_HEIGHT:
                    if not board.game_over:
                        if not vs_ai or (vs_ai and board.turn == PieceColor.WHITE):
                            board.select_by_mouse(mx, my)
                px = SCREEN_W - SIDE_PANEL_W - 30
                py = 80
                play_rect = pygame.Rect(px + 16, SCREEN_H - 120, SIDE_PANEL_W - 32, 40)
                if play_rect.collidepoint((mx,my)) and board.game_over:
                    board = Board()

        if (not board.game_over and vs_ai and 
            board.turn == PieceColor.BLACK and 
            not board.ai_thinking):
            
            board.ai_thinking = True
            
            draw_background()
            draw_title_panel()
            draw_board(board)
            draw_info(board, ai, spinner_angle)
            pygame.display.flip()

            best = ai.get_best_move(board)
            if best:
                fr_fc, to = best
                fr, fc = fr_fc
                tr, tc = to
                
                board.last_move = ((fr, fc), (tr, tc))
                board.move_history.append(board.last_move)
                board.animate_and_apply(fr, fc, tr, tc)
                board.turn = PieceColor.WHITE
                board.check_game_over()
            
            board.ai_thinking = False

        draw_background()
        panel_rect = draw_title_panel()
        draw_board(board)
        draw_info(board, ai, spinner_angle)

        px = SCREEN_W - SIDE_PANEL_W - 30
        py = 80
        mode_text = "Chế độ: Người vs Máy" if vs_ai else "Chế độ: Người vs Người"
        screen.blit(NORMAL_FONT.render(mode_text, True, WHITE), (px + 16, py + 86))
        screen.blit(NORMAL_FONT.render("Nhấn M để đổi chế độ", True, SILVER), (px + 16, py + 146))

        if board.game_over:
            px = SCREEN_W - SIDE_PANEL_W - 30
            play_rect = pygame.Rect(px + 16, SCREEN_H - 120, SIDE_PANEL_W - 32, 40)
            pygame.draw.rect(screen, (100,180,230), play_rect, border_radius=8)
            pygame.draw.rect(screen, WHITE, play_rect, 2, border_radius=8)
            txt = NORMAL_FONT.render("Bắt đầu  lại (hoặc nhấn R)", True, WHITE)
            screen.blit(txt, (play_rect.x + play_rect.width//2 - txt.get_width()//2, play_rect.y + play_rect.height//2 - txt.get_height()//2))

        pygame.display.flip()
        spinner_angle = (spinner_angle + 8) % 360

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
