#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jan 26 19:22:38 2018

@author: bjh7790
"""
import random
import copy
import itertools
import operator
import time

Size = (10,10)
Num = 10

# Create a Answer with random mines
def CreateGame(Size = Size, Num = Num):
    Ans = [[0]*Size[0] for n in range(Size[1])]
    x = [i for i in range(1, Size[0]*Size[1])]
    RandomListForMine = random.sample(x,Num)
    for i in RandomListForMine:
        x = i // Size[0]
        y = i % Size[0]
        Ans[x][y] = 1
    return Ans
    
# A function to print pretty
def PrintCurrentStat(CurrentStat):
    i = 1
    j = 1
    print('    ', end ='')
    for idx in CurrentStat[0]:
        print(j, end =' ')
        j=j+1
    print('\n')
    for row in CurrentStat:
        print(i, end = '   ')
        i=i+1
        for elem in row:
            print(elem, end=' ')
        print()

# Create Neighbor numbers
def MakeNeighborMatrix(Ans):
    Neigh = [[0]*Size[0] for n in range(Size[1])]
    for row in range(Size[1]):
        for elem in range(Size[0]):
            for i in FindNeighbor((row,elem)):
                Neigh[row][elem] += Ans[i[0]][i[1]]
    return Neigh

def FindNeighbor(location, Size = Size):
    x = location[0]
    y = location[1]
    N = [(x-1,y-1),(x,y-1),(x+1,y-1),(x-1,y),(x+1,y),(x-1,y+1),(x,y+1),(x+1,y+1)]
    if x == 0:
        N.remove((x-1,y-1))
        N.remove((x-1,y))
        N.remove((x-1,y+1))
    if x == Size[1]-1:
        N.remove((x+1,y-1))
        N.remove((x+1,y))
        N.remove((x+1,y+1))
    if y == 0:
        try:
            N.remove((x+1,y-1))
        except:
            ...
        N.remove((x,y-1))
        try:
            N.remove((x-1,y-1))
        except:
            ...
    if y == Size[0]-1:
        try:
            N.remove((x+1,y+1))
        except:
            ...
        N.remove((x,y+1))
        try:
            N.remove((x-1,y+1))
        except:
            ...
    return N

#Start the game
#Ans is consisted of 0 and 1; 1 for mine
#Neigh has numbers of mines in one's neighbor(max 8)
#Open is what player can see. 0 for not opened cells, '/' for empty cells, number for cells that has mines around it
#Players can not check mines yet
def StartGame(Size = Size, Num = Num):
    Ans = CreateGame()
    Neigh = MakeNeighborMatrix(Ans)
    Open = [[0]*Size[0] for n in range(Size[1])]
    Game = True
    while Game:
        if sum(x.count(0) for x in Open) == Num:
            print("End!!")
            PrintCurrentStat(Ans)
            return 'success'
        print("select place to click // -1,-1 to break // -2,-2 for help")
        x,y = (int(elem) for elem in input().split())
        x = x-1
        y = y-1
        if (x,y) == (-2,-2):
            break
        if (x,y) == (-3,-3):
            a,b = Help(Ans,Open,Neigh)
            print("Help clicked (",a,',',b,")!")
            print("---------------------------")
            if (a>Size[1]-1) or (b>Size[0]-1) or (a<0) or (b<0):
                print("out of range")
                print("Choose again")
                continue
            if Open[a][b] != 0:
                print("Already Clicked")
                print("Choose Again")
                continue
            if Ans[a][b] == 1:
                print("Fail")
                PrintCurrentStat(Ans)
                return 'fail'
            Open = Click(a,b,Ans,Open,Neigh)
            PrintCurrentStat(Open)
            continue
        else:
            if (x>Size[1]-1) or (y>Size[0]-1) or (x<0) or (y<0):
                print("out of range")
                print("Choose again")
                continue
            if Open[x][y] != 0:
                print("Already Clicked")
                print("Choose Again")
                continue
            if Ans[x][y] == 1:
                print("Fail")
                PrintCurrentStat(Ans)
                return 'fail'
            Open = Click(x,y,Ans,Open,Neigh)
            PrintCurrentStat(Open)
    return 0

#Silence version of StartGame for performance check
def StartGame_Silence(Size = Size, Num = Num):
    Ans, p = CreateGame()
    Neigh = MakeNeighborMatrix(Ans)
    Open = [[0]*Size[0] for n in range(Size[1])]
    Game = True
    ticker = 0
    while Game:
        if sum(x.count(0) for x in Open) == Num:
            return 'success', Ans
        a,b = Help_Silence(Ans,Open,Neigh)
        if (a>Size[1]-1) or (b>Size[0]-1) or (a<0) or (b<0):
            continue
            ticker += 1
        if Open[a][b] != 0:
            continue
            ticker += 1
        if Ans[a][b] == 1:
            return 'fail', Ans
        if ticker > 10:
            break
        Open = Click(a,b,Ans,Open,Neigh)
    return 0, Ans

def Click(x,y,Ans,Open,Neigh):
    S=[(x,y)]
    while S:
        (x,y) = S.pop()
        if Neigh[x][y] != 0:
            Open[x][y] = Neigh[x][y]
        elif Open[x][y] != 0:
            continue
        else:
            Open[x][y] = '/'
            for i in FindNeighbor((x,y)):
                S.append(i)
    return Open

#minesweeper AI : appears when player clicks for help
#Help is made up with three parts; each named phase1, phase2, phase3
#Phase1 converts Open to Open2; checking where mine is - by if cell named 2 only has 2 empty cells around it.. they have mines
#Phase2 checks places that doesn't have mines - by if cell named 2 already have 2 mines around it.. the rest is mine free
#Phase3 calculates all possible mine arrangements; and calculates the odds of a cell to have mine. Returns with the least odds. If it is 50%.. hope it is the lucky guess
def Help(Ans,Open,Neigh):
    print("---------------------------")
    print("Hi, this is minesweeper AI")
    print("Well, lets first see what you have done!\n")
    Open2 = Phase1(Open)
    PrintCurrentStat(Open2)
    print("")
    print("Okay so lets click some obvious places; if there is one")
    (x,y) = Phase2(Open2)
    if (x,y) != (-1,-1):
        return x,y
    else:
        print("")
        print("No obvious places though..")
        print("We must go into some calculations then")
        (x,y) = Phase3(Open2)
        return x,y
    
def Help_Silence(Ans,Open,Neigh):
    Open2 = Phase1(Open)
    (x,y) = Phase2(Open2)
    if (x,y) != (-1,-1):
        return x,y
    else:
        (x,y) = Phase3_Silence(Open2)
        return x,y

def Phase1(Open,Size = Size):
    Open2 = copy.deepcopy(Open)
    for row in range(Size[1]):
        for elem in range(Size[0]):
            num = 0
            for i in FindNeighbor((row,elem)):
                if Open[i[0]][i[1]] == 0:
                    num += 1
            if num == Open[row][elem]:
                for i in FindNeighbor((row,elem)):
                    if Open[i[0]][i[1]] == 0:
                        Open2[i[0]][i[1]] = '*'
    return Open2

def Phase2(Open2):
    for row in range(Size[1]):
        for elem in range(Size[0]):
            if (Open2[row][elem] == '*') or (Open2[row][elem] == 0):
                continue
            num = 0
            obvpla = []
            for i in FindNeighbor((row,elem)):
                if Open2[i[0]][i[1]] == '*':
                    num += 1
                if Open2[i[0]][i[1]] == 0:
                    obvpla.append(i)
            if num == Open2[row][elem]:
                if len(obvpla) !=0:
                    return obvpla[0]
    return (-1,-1)

# empty is a dictionary to sum up the odds of each cells being mine
# border is opened cells we need to consider.
# border2 is not yet opened cells we need to consider. - Not yet opened cells except border2 all has same possibility so no need to calculate all.
# possAnsBase contains mines already discovered.
# We add one of possiblemines to possAnsBase to get possibleAnswer
# If possibleAnswer satisfies all the cells in border then it is indeed a possible Answer
def Phase3(Open2, Size = Size, Num = Num):
    possAnsBase = [[0]*Size[0] for n in range(Size[1])]
    empty = {}
    border = []
    border2 = []
    number = []
    mines = 0
    totalnum = 0
    for row in range(Size[1]):
        for elem in range(Size[0]):
            if Open2[row][elem] == '*':
                mines += 1
                possAnsBase[row][elem] = '*'
            elif Open2[row][elem] == 0:
                empty[(row, elem)] = 0
                for i in FindNeighbor((row,elem)):
                    if (i not in border) and (Open2[i[0]][i[1]] != '*'):
                        border.append(i)
            else:
                number.append((row,elem))
                for i in FindNeighbor((row,elem)):
                    if i not in border2:
                        border2.append(i)
    
    if (mines == 0) and (Open2[0][0] == 0):
        return (0,0)
    
    minesleft = Num - mines
    emptylist = list(empty.keys())
    for i in emptylist:
        if i in border:
            border.remove(i)
    for i in border2[:]:
        if i not in empty:
            border2.remove(i)
    
    possiblemines = list(itertools.chain.from_iterable(itertools.combinations(border2, r) for r in range(min(len(border2)+1,minesleft+1))))
    
    for i in possiblemines:
        resultfori = True
        possAns = copy.deepcopy(possAnsBase)
        for elem in i:
            possAns[elem[0]][elem[1]] = '*'
        for j in border:
            n = 0
            for k in FindNeighbor(j):
                if possAns[k[0]][k[1]] == '*':
                    n += 1
            if n != Open2[j[0]][j[1]]:
                resultfori = False
                break
        if resultfori == True:
            totalnum += 1
            for elem in i:
                empty[elem] += 1
    
    if totalnum == 0:
        return (-1,-1)
    
    for elem in empty:
        empty[elem] = empty[elem]*100.000/totalnum
    
    if (len(empty.keys()) != len(border2)):
        a = (minesleft*100.0 - sum(empty.values()))/(len(empty.keys()) - len(border2) )
        for i in list(empty.keys()):
            if i not in border2:
                empty[i] = a
    
    sorted_x = sorted(empty.items(), key=operator.itemgetter(1))
    print("---------------------------")
    print("calculations done")
    print("some top ranked are...")
    for idx in range(len(emptylist)):
        print(idx+1, end = ' ')
        print(sorted_x[idx][0], end = ' : ')
        print(sorted_x[idx][1])
    return sorted_x[0][0]

def Phase3_Silence(Open2, Size = Size, Num = Num):
    possAnsBase = [[0]*Size[0] for n in range(Size[1])]
    empty = {}
    border = []
    border2 = []
    number = []
    mines = 0
    totalnum = 0
    for row in range(Size[1]):
        for elem in range(Size[0]):
            if Open2[row][elem] == '*':
                mines += 1
                possAnsBase[row][elem] = '*'
            elif Open2[row][elem] == 0:
                empty[(row, elem)] = 0
                for i in FindNeighbor((row,elem)):
                    if (i not in border) and (Open2[i[0]][i[1]] != '*'):
                        border.append(i)
            else:
                number.append((row,elem))
                for i in FindNeighbor((row,elem)):
                    if i not in border2:
                        border2.append(i)
    
    if (mines == 0) and (Open2[0][0] == 0):
        return (0,0)
    
    minesleft = Num - mines
    emptylist = list(empty.keys())
    for i in emptylist:
        if i in border:
            border.remove(i)
    for i in border2[:]:
        if i not in empty:
            border2.remove(i)
    
    possiblemines = list(itertools.chain.from_iterable(itertools.combinations(border2, r) for r in range(min(len(border2)+1,minesleft+1))))
    
    for i in possiblemines:
        resultfori = True
        possAns = copy.deepcopy(possAnsBase)
        for elem in i:
            possAns[elem[0]][elem[1]] = '*'
        for j in border:
            n = 0
            for k in FindNeighbor(j):
                if possAns[k[0]][k[1]] == '*':
                    n += 1
            if n != Open2[j[0]][j[1]]:
                resultfori = False
                break
        if resultfori == True:
            totalnum += 1
            for elem in i:
                empty[elem] += 1
    
    if totalnum == 0:
        return (-1,-1)
    
    for elem in empty:
        empty[elem] = empty[elem]*100.000/totalnum
        
    if (len(empty.keys()) != len(border2)):
        a = (minesleft*100.0 - sum(empty.values()))/(len(empty.keys()) - len(border2) )
        for i in list(empty.keys()):
            if i not in border2:
                empty[i] = a
                
    sorted_x = sorted(empty.items(), key=operator.itemgetter(1))
    return sorted_x[0][0]

# A simple function for performance check. It makes the computer solve n minesweeper game.
# In the file ms.txt, it contains index number, the answer sheet, success or not, and the time passed
# In the console, it prints the index number, and the time passed.    
def Check(n):
    a = {}
    timems = []
    a['success'] = 0
    a['fail'] = 0
    a[0] = 0
    f = open("/home/bjh7790/bsj/minesweeper/ms.txt", 'w')
    t0 = time.time()
    for idx in range(n):
        f.write(str(idx))
        f.write("\t")
        print(idx)
        result, Ans = StartGame_Silence()
        a[result] += 1
        f.writelines('\t'.join(str(i) + '\n' for i in Ans))
        f.write("\n")
        t1 = time.time()
        timems.append(t1-t0)
        f.write(str(t1-t0))
        f.write(result)
        f.write('\n')
        print(t1-t0)
        t0 = t1
    print(a['success']/n)
    f.close()
    print(sum(timems) / len(timems) )
a = Check(100)