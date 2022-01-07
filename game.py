import pygame as pg
from pygame.locals import *
import random

#ウィンドウサイズ設定
WIDTH  = 1228
HEIGHT = 614   

#バックグラウンドクラス
class Background:
    def __init__(self):        
        self.image = pg.image.load("png/bg/full-bg.png")
        self.image = pg.transform.scale(self.image,(WIDTH,HEIGHT))
    def update(self,screen):
        screen.blit(self.image,(0,0))
       
#パドルクラス（プレイヤー）
class Paddle(pg.sprite.Sprite):
    def __init__(self, x, y):
        pg.sprite.Sprite.__init__(self)
        self.paddle_width = 126
        self.paddle_height = 54
        self.image = pg.image.load("png/bar/1.png")
        self.mask = pg.mask.from_surface(self.image)
        #画像のサイズをrectで取得する、rext.center位置の設定
        self.rect = self.image.get_rect()
        self.rect.center = [x,y]   
       
    def update(self):
        #マウス操作で移動するように設定        
        dx = pg.mouse.get_pos()[0]
        self.rect.x = dx
        #画面両端から先にいけないように設定
        if self.rect.x < 0:
            self.rect.x = 0
        if self.rect.topright[0] >= WIDTH:
            self.rect.x = WIDTH - self.paddle_width
        

#ボールクラス
class Ball(pg.sprite.Sprite):
    def __init__(self, x, y):
        pg.sprite.Sprite.__init__(self)
        #画像のサイズからサイズ調整
        self.width = 24
        self.height = 24
        self.image = pg.image.load('png/ball/ball.png')
        self.mask = pg.mask.from_surface(self.image)
        #画像のサイズをrectで取得する、rext.center位置の設定
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]
        #ボールの速度を設定。
        self.vel_x = 9
        self.vel_y = 9

    #ボールの初期位置を関数で設定しておく。初期値はプレイヤーの上。
    # 引数でプレイヤーのrectを指定し、その値をボールの初期値に返す
    def init_position(self,paddlex,paddley):
        self.rect.x = paddlex - self.width + self.width
        self.rect.y = paddley - self.height - self.height
        return self.rect.x, self.rect.y
    
    #ボールがプレイヤーより下にいった時の処理。killでグループから削除（後ほどグループの説明が出てきます）
    def miss(self):
        self.kill()

    def draw_lives(self,screen):
        self.image = pg.image.load('png/ball/ball.png')
        self.image.set_colorkey((0,0,0))
        screen.blit(self.image,(10,HEIGHT - 50))

    #毎フレームごとのボールの移動処理
    def update(self):  
        #移動量、方向を追加      
        self.rect.x += self.vel_x
        self.rect.y -= self.vel_y
        #端に来た時の反射を設定（速度に-1をかけると速度が逆の値になるので）
        if self.rect.centerx < 0 or self.rect.centerx > WIDTH:
            self.vel_x *= -1
        if self.rect.topleft[1] < 0 or self.rect.topright[1] < 0:
            self.vel_y *= -1
        
            
            
#ブロッククラス
class Block(pg.sprite.Sprite):
    def __init__(self,x,y,index):
        pg.sprite.Sprite.__init__(self)
        #画像のサイズからサイズ調整
        self.block_width = 52
        self.block_height = 52
        
        #4枚の画像があるのでリストに格納
        self.images = [pg.image.load(f"png/blocks/{i}.png") for i in range(1,5)]
        
        #image変数を設定し画像を１枚ずつ取り出せるようにしておく
        self.image = self.images[index]
        self.mask = pg.mask.from_surface(self.image)
        #画像のサイズをrectで取得する、rext.topleft位置の設定
        self.rect = self.image.get_rect()
        self.rect.topleft = [x,y]


#ブロック配置リスト
#forで縦4、横20　のブロック並びに設定。好きな数に変更しても良いです。randomを使用すれば毎回違う並びになります。
blocks = [[random.randint(0,3) for _ in range(20)] for _ in range(4)] 
#下の6行と上の1行は同じ内容です。記述方法が違うだけです。
# blocks = []
# for i in range(4):
#     temp = []
#     for j in range(20):
#         temp.append(random.randint(0,3))
#     blocks.append(temp)


#ゲームクラス
class Game:
    def __init__(self):
        pg.init()
        self.clock = pg.time.Clock()
        self.fps = 30
        
        self.block_size = 52
        
        self.life = 1
        
        #プレイ状況を最初はfalseにしておく
        self.play = False
        
        #画面surfaceの設定
        self.screen = pg.display.set_mode((WIDTH,HEIGHT))
        #ゲームのタイトル
        pg.display.set_caption('BLOCK KUZUSHI')
        
        #バックグラウンドのインスタンス化
        self.bg = Background()

        #インスタンス化およびグループ化し、インスタンス化した物をグループに追加
        self.paddle = Paddle(WIDTH / 2, HEIGHT - 100)
        self.paddle_group = pg.sprite.GroupSingle(self.paddle)

        #インスタンス化およびグループ化し、インスタンス化した物をグループに追加。
        self.ball = Ball(self.paddle.rect.centerx,self.paddle.rect.centery)
        self.ball_group = pg.sprite.GroupSingle(self.ball)

        #インスタンス化およびグループ化し、インスタンス化した物をグループに追加。
        self.block_group = pg.sprite.Group()

        #2重のforループでblocksリストから参照します。
        col_counter = 0
        for col in blocks:
            row_counter = 0
            for row in col: 
                #blocksの値が0ならindexを0に指定します。すると表示されるブロックは青色になります。 1～3もそれぞれに対応させて設定              
                if row == 0:
                    #Blockのinit関数で位置とインデックスを引数に渡していたので指定します。
                    self.block = Block(100 + self.block_size * row_counter, self.block_size * col_counter, 0)
                    self.block_group.add(self.block)
                if row == 1:
                    self.block = Block(100 + self.block_size * row_counter, self.block_size * col_counter, 1)
                    self.block_group.add(self.block)
                if row == 2:
                    self.block = Block(100 + self.block_size * row_counter, self.block_size * col_counter, 2)
                    self.block_group.add(self.block)
                if row == 3:
                    self.block = Block(100 + self.block_size * row_counter, self.block_size * col_counter, 3)
                    self.block_group.add(self.block)
                row_counter += 1
            col_counter += 1       


    #メインループ処理
    def main(self):
        running = True
        while running:
            for event in pg.event.get():
                #×印かエスケープキーでゲーム中断
                if event.type == pg.QUIT:
                    running = False
                if event.type == KEYDOWN:
                    if event.key == K_ESCAPE:
                        running = False
                    
                #マウスのボタンでスタートさせる処理
                if event.type == MOUSEBUTTONDOWN:
                    self.play = True
                    
            #マウスカーソルを消去
            pg.mouse.set_visible(False)
            #バックグラウンドの更新
            self.bg.update(self.screen)            
            
            #グループの描画処理
            self.block_group.draw(self.screen)
            self.ball_group.draw(self.screen)
            self.paddle_group.draw(self.screen)
            self.ball.draw_lives(self.screen)
            #パドルの更新
            self.paddle_group.update()            
            #ボールの初期位置の処理。ゲームが始まっていないなら、ボールは初期位置
            if not self.play:
                self.ball.init_position(self.paddle.rect.centerx,self.paddle.rect.centery)
            #ゲーム開始後の処理
            if self.play: 
                #ボールの更新
                self.ball_group.update()
                
                #ボールとブロックの衝突判定
                detect_range = 10
                for block in self.block_group:                                  
                    if pg.sprite.collide_rect(self.ball,block):
                        if abs(block.rect.top - self.ball.rect.bottom) < detect_range and self.ball.vel_y < 0:
                            self.ball.vel_y *= -1 
                            block.kill()
                        if abs(block.rect.bottom - self.ball.rect.top) < detect_range and self.ball.vel_y > 0:
                            self.ball.vel_y *= -1
                            block.kill()
                        if abs(block.rect.right - self.ball.rect.left) < detect_range and self.ball.vel_x < 0:
                            self.ball.vel_x *= -1
                            block.kill()
                        if abs(block.rect.left - self.ball.rect.right) < detect_range and self.ball.vel_x > 0:
                            self.ball.vel_x *= -1
                            block.kill()
                        
                #ボールとプレイヤーの衝突判定 
                if pg.sprite.collide_rect(self.ball,self.paddle):
                    if abs(self.paddle.rect.top - self.ball.rect.bottom) < detect_range and self.ball.vel_y < 0:
                        self.ball.vel_y *= -1
                    if abs(self.paddle.rect.right - self.ball.rect.left) < detect_range and self.ball.vel_x < 0:
                        self.ball.vel_x *= -1
                    if abs(self.paddle.rect.left - self.ball.rect.right) < detect_range and self.ball.vel_x > 0:
                        self.ball.vel_x *= -1
                
                #ボールが画面下端より下にいったら上で設定したmiss関数が実行される
                if self.ball.rect.y > HEIGHT:
                    self.ball.miss()
                    if self.life > 0:
                        self.play = False
                        self.ball = Ball(self.paddle.rect.centerx,self.paddle.rect.centery)
                        self.ball_group = pg.sprite.GroupSingle(self.ball)
                        self.life -= 1
                    
            self.clock.tick(self.fps)
            pg.display.update()
        pg.quit()

#ゲームクラスをインスタンス化してmain関数で実行
game = Game()
game.main()