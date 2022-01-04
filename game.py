import pygame as pg
from pygame.locals import *
import random

#画像のサイズからサイズ調整　3072＊1536
WIDTH  = int(3072 / 2.5)
HEIGHT = int(1536 / 2.5)

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
        #画像のサイズよりサイズ調整
        self.paddle_width = int(1518 / 12)
        self.paddle_height = int(642 / 12)
        self.image = pg.image.load("png/bar/1.png")
        self.image = pg.transform.scale(self.image,(self.paddle_width,self.paddle_height))
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
        width = int(414 / 15)
        height = int(408 / 15)
        self.image = pg.image.load('png/bullet/bullet4.png')
        self.image = pg.transform.scale(self.image,(width,height))
        #画像のサイズをrectで取得する、rext.center位置の設定
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]
        #ボールの速度を設定。最高速度も設定しておく
        self.vel_x = 7
        self.vel_y = 9
        self.speed = 1
        self.maxspeed = 15   

    #ボールの初期位置を関数で設定しておく。初期値はプレイヤーの上。引数でプレイヤーのrectを指定し、その値をボールの初期値に返す
    def init_position(self,paddlex,paddley):
        self.rect.x = paddlex
        self.rect.y = paddley
        return self.rect.x, self.rect.y
    
    #ボールがプレイヤーより下にいった時の処理。killでグループから削除（後ほどグループの説明が出てきます）
    def miss(self):
        self.kill()

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
        #ボールが画面下端より下にいったら上で設定したmiss関数が実行される
        if self.rect.y > HEIGHT:
            self.miss()
  
            
#ブロッククラス
class Block(pg.sprite.Sprite):
    def __init__(self,x,y,index):
        pg.sprite.Sprite.__init__(self)
        #画像のサイズからサイズ調整
        self.block_width = int(522 / 10)
        self.block_height = int(522 / 10)
        #４枚の画像があるのでリストに格納していく。同時にサイズ調整も行う
        self.images = []
        for i in range(1,5):
            img = pg.image.load(f"png/blocks/{i}.png")
            img = pg.transform.scale(img,(self.block_width,self.block_height))
            self.images.append(img)
        
        #image変数し画像を１枚ずつ取り出せるようにしておく
        self.image = self.images[index]
        #画像のサイズをrectで取得する、rext.topleft位置の設定
        self.rect = self.image.get_rect()
        self.rect.topleft = [x,y]


#ブロック配置用マップ
#空のリストを用意します
blocks = []  
#forで縦４、横15　のブロック並びに設定。好きな数に変更しても良いです。randomを使用すれば毎回違う並びになります。
for col in range(4):
    data = []
    for row in range(18):
        data.append(random.randint(0,3))
    blocks.append(data)
# 上のfor文で以下のようなリストができます。リスト内の数字は毎回ランダムです。
# blocks =[
#     [3, 2, 1, 1, 2, 2, 1, 1, 3, 0, 2, 0, 2, 0, 1], 
#     [2, 0, 2, 0, 3, 1, 3, 1, 1, 0, 2, 2, 2, 0, 3], 
#     [2, 3, 2, 3, 2, 0, 2, 2, 3, 2, 3, 0, 1, 2, 3], 
#     [1, 3, 0, 3, 3, 1, 1, 2, 0, 1, 2, 1, 3, 2, 1]
#     ]

#ゲームクラス
class Game:
    def __init__(self):
        pg.init()
        self.clock = pg.time.Clock()
        self.fps = 30
        #プレイ状況を最初はfalseにしておく
        self.play = False
        #画面surfaceの設定
        self.screen = pg.display.set_mode((WIDTH,HEIGHT))
        #ゲームのタイトル
        pg.display.set_caption('BLOCK KUZUSHI')
        
        #バックグラウンドのインスタンス化
        self.bg = Background()

        #インスタンス化およびグループ化し、インスタンス化した物をグループに追加
        self.paddle = Paddle(WIDTH / 2, HEIGHT - 80)
        self.paddle_group = pg.sprite.GroupSingle(self.paddle)

        #インスタンス化およびグループ化し、インスタンス化した物をグループに追加。
        #クラス内で出てきたkill()を行うとこのグループから外れます（画面の描画が消えます）
        self.ball = Ball(WIDTH /3, HEIGHT / 2)
        self.ball_group = pg.sprite.GroupSingle(self.ball)

        #インスタンス化およびグループ化し、インスタンス化した物をグループに追加。
        self.block_group = pg.sprite.Group()
        #Blockのinit関数で位置とインデックスを引数に渡していたので指定します。
        #２重のforループでmapリストから参照します。
        col_counter = 0
        for col in blocks:
            row_counter = 0
            for row in col: 
                #mapの値が0ならindexを0に指定します。すると表示されるブロックは青色になります。 1～3もそれぞれに対応させて設定              
                if row == 0:
                    self.block = Block(120 + 52 * row_counter, 52 * col_counter, 0)
                    self.block_group.add(self.block)
                if row == 1:
                    self.block = Block(120 + 52 * row_counter, 52 * col_counter, 1)
                    self.block_group.add(self.block)
                if row == 2:
                    self.block = Block(120 + 52 * row_counter, 52 * col_counter, 2)
                    self.block_group.add(self.block)
                if row == 3:
                    self.block = Block(120 + 52 * row_counter, 52 * col_counter, 3)
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
                   
            #バックグラウンドの更新
            self.bg.update(self.screen)            
            
            #グループの描画処理
            self.block_group.draw(self.screen)
            self.ball_group.draw(self.screen)
            self.paddle_group.draw(self.screen)
            
            #パドルの更新
            self.paddle_group.update()            

            #ボールの初期位置の処理。ゲームが始まっていないなら、ボールは初期位置
            if not self.play:
                self.ball.init_position(self.paddle.rect.centerx,self.paddle.rect.centery - 50)
            
            #ゲーム開始後の処理
            if self.play: 
                #ボールの更新
                self.ball_group.update()
                #ボールとブロックの衝突判定
                # groupcollideをforでループさせると衝突一回毎の処理が行える
                # 引数のtrue,falseで衝突時にkill（削除する）か設定できる
                detect_range = 10                                  
                collide_list = pg.sprite.groupcollide(self.ball_group,self.block_group,False,True)
                for collide in collide_list:
                    #衝突したらボールを反射させて速度を追加する
                    self.ball.vel_y *= -1
                    if self.ball.speed <= self.ball.maxspeed:
                        self.ball.vel_y += self.ball.speed
                        
                #ボールとプレイヤーの衝突判定    
                paddle_collide = pg.sprite.collide_rect(self.ball,self.paddle)
                
                if paddle_collide:
                    #衝突したらボールを反射させて速度を追加する               
                    self.ball.vel_y *= -1
                    if self.ball.speed <= self.ball.maxspeed:
                        self.ball.vel_y += self.ball.speed
                    
            self.clock.tick(self.fps)
            pg.display.update()
        pg.quit()

#ゲームクラスをインスタンス化してmain関数で実行
game = Game()
game.main()