import sys
import argparse
import json
import random
import socket

sys.path.append("../PythonAdvanced2BA/AIproject")
sys.path.append("../simpleai")

from kingandassassins import KingAndAssassinsState
from lib import game
from simpleai.search import SearchProblem, breadth_first




class KingAndAssassinsJoshua(game.GameClient):
    '''Class representing a client for the King & Assassins game'''

    def __init__(self, name, server, verbose=False):
        self.__name = name
        self.turn = 15
        super().__init__(server, KingAndAssassinsState, verbose=verbose)


    def _handle(self, message):
        pass

    def _getcoord(self, coord):
        return tuple(coord[i] + KingAndAssassinsState.DIRECTIONS[coord[2]][i] for i in range(2))

    #def kingplace(self):
        #state = state2._state['visible']
        #for i in range(10):
            #for j in range(10):
                #if state['people'][i][j] == 'king':
                    #return (i,j)

    def aftermovedistanceking(self,x,y,d):
        xk,yk = 2,2
        if d == 'N':
            return (abs(xk-x)+abs(yk-y),abs(xk-x)+abs(yk-(y-1)))
        if d == 'S':
            return (abs(xk-x)+abs(yk-y),abs(xk-x)+abs(yk-(y+1)))
        if d == 'W':
            return (abs(xk-x)+abs(yk-y),abs(xk-(x-1))+abs(yk-y))
        if d == 'E':
            return (abs(xk-x)+abs(yk-y),abs(xk-(x+1))+abs(yk-y))

    def aftermovedistancegate(self,x,y,d):
        x1,y1,x2,y2 = 4,1,4,1
        if d == 'N':
            return (abs(x1-x)+abs(y1-y),abs(x1-x)+abs(y1-(y-1)))
        if d == 'S':
            return (abs(x1-x)+abs(y1-y),abs(x1-x)+abs(y1-(y+1)))
        if d == 'W':
            return (abs(x1-x)+abs(y1-y),abs(x1-(x-1))+abs(y1-y))
        if d == 'E':
            return (abs(x1-x)+abs(y1-y),abs(x1-(x+1))+abs(y1-y))

    def update(self, move,state):
        people = state['people']
        if move[0] == 'move':
            x, y, d = int(move[1]), int(move[2]), move[3]
            nx, ny = self._getcoord((x, y, d))
            p = people[x][y]
            people[x][y] = None
            people[nx][ny] = p
        if move[0] == 'arrest':
            x, y, d = int(move[1]), int(move[2]), move[3]
            nx, ny = self._getcoord((x, y, d))
            people[nx][ny] = None
        if move[0] == 'kill':
            x, y, d = int(move[1]), int(move[2]), move[3]
            nx, ny = self._getcoord((x, y, d))
            people[nx][ny] = None
        state['people'] = people
        return state

    def ordermovement(self,moves,arrest):
        possiblemove =[]
        for element in moves:
            if element[0] == 'kill':
                return (element,arrest)
            if (element[0] == 'arrest') and (arrest == True):
                arrest = False
                return (element,arrest)
            if element[0] == 'move':
                before , after = self.aftermovedistanceking(element[1],element[2],element[3])
                if before > after:
                    possiblemove.append(element)
        return (possiblemove[random.randint(0,len(possiblemove)-1)],arrest)


    def _nextmove(self, state2):
        state = state2._state['visible']
        if state['card'] is None:
            return json.dumps({'assassins': [state['people'][2][1], state['people'][3][4],  state['people'][5][5]]}, separators=(',', ':'))
        else:
            self.turn = self.turn - 1
        if self._playernb == 0:
            if self.turn == 14:
                return json.dumps({'actions': []}, separators=(',', ':'))
                #return json.dumps({'actions': [('reveal', 2, 1),('reveal', 3, 4),('move',2,1,'S'),('move',3,4,'N'),('move',2,4,'N'),('kill', 1,4, 'W'),('kill', 3,1, 'W')]}, separators=(',', ':'))
            else:
                return json.dumps({'actions': []}, separators=(',', ':'))
        else:
            paking,paknight = state['card'][0],state['card'][1]
            movelist = []
            playingstate = state
            arrest = state['card'][2]
            while paknight > 0:
                result = KnightPlayer(playingstate).action("knight")
                movement,arrest = self.ordermovement(result,arrest)
                movelist.append(movement)
                paknight = paknight - 1
                playingstate = self.update(movement,playingstate)
            while paking > 0:
                result = KnightPlayer(playingstate).action("king")
                if not (len(result) == 0):
                    for element in result:
                        before,after = self.aftermovedistancegate(element[1],element[2],element[3])
                        if before > after :
                            movement = element
                            break
                    movelist.append(movement)
                    playingstate = self.update(movement,playingstate)
                else:
                    break
                paking = paking - 1
            try:
                return json.dumps({'actions': movelist}, separators=(',', ':'))
            except:
                return json.dumps({'actions': []}, separators=(',', ':'))




class KnightPlayer():
    def __init__(self,state):
        self.__state = state['people']
        self.__card =  state['card']
        self.__population ={'monk', 'plumwoman', 'appleman', 'hooker', 'fishwoman', 'butcher','blacksmith', 'shepherd', 'squire', 'carpenter', 'witchhunter', 'farmer'}

    def checkingknightmove(self,i,j,direction):
        if self.__state[i][j] == None:
            return True
        if self.__state[i][j] == 'knight':
            return True
        else:
            if direction == 'N' and i>0:
                return self.checkingknightmove(i-1,j,direction)
            if direction == 'S' and i<9:
                return self.checkingknightmove(i+1,j,direction)
            if direction == 'E' and j<9:
                return self.checkingknightmove(i,j+1,direction)
            if direction == 'W' and j>0:
                return self.checkingknightmove(i,j-1,direction)
        return False

    def checkingaround(self,i,j,direction):
        if direction == 'N' and i>0:
            return self.__state[i-1][j]
        if direction == 'S' and i<9:
            return self.__state[i+1][j]
        if direction == 'E' and j<9:
            return self.__state[i][j+1]
        if direction == 'W' and j>0:
            return self.__state[i][j-1]
        else:
            return False

    def action(self,personne):
        result = []
        for i in range(10):
            for j in range(10):
                if self.__state[i][j] == 'knight' and personne == "knight":
                    for element in ['N','S','E','W']:
                        if self.checkingknightmove(i,j,element):
                            result.append(('move',i,j,element))
                        if self.checkingaround(i,j,element) == 'assassins':
                            result.append(('kill',i,j,element))
                        if self.__card[2] == True:
                            if self.checkingaround(i,j,element) in self.__population:
                                result.append(('arrest',i,j,element))
                if self.__state[i][j] == 'king' and personne == "king":
                    for element in ['N','S','E','W']:
                        if self.checkingaround(i,j,element) == None:
                            result.append(('move',i,j,element))
        return result

if __name__ == '__main__':
    # Create the top-level parser
    parser = argparse.ArgumentParser(description='King & Assassins game')
    subparsers = parser.add_subparsers(
        description='server client',
        help='King & Assassins game components',
        dest='component'
    )

    # Create the parser for the 'server' subcommand
    server_parser = subparsers.add_parser('server', help='launch a server')
    server_parser.add_argument('--host', help='hostname (default: localhost)', default='localhost')
    server_parser.add_argument('--port', help='port to listen on (default: 5000)', default=5000)
    server_parser.add_argument('-v', '--verbose', action='store_true')
    # Create the parser for the 'client' subcommand
    client_parser = subparsers.add_parser('client', help='launch a client')
    client_parser.add_argument('name', help='name of the player')
    client_parser.add_argument('--host', help='hostname of the server (default: localhost)',
                               default=socket.gethostbyname(socket.gethostname()))
    client_parser.add_argument('--port', help='port of the server (default: 5000)', default=5000)
    client_parser.add_argument('-v', '--verbose', action='store_true')
    # Parse the arguments of sys.args
    args = parser.parse_args()

    if args.component == 'server':
        KingAndAssassinsServer(verbose=args.verbose).run()
    else:
        KingAndAssassinsJoshua(args.name, (args.host, args.port), verbose=args.verbose)
