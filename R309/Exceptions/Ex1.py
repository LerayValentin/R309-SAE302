def divEntier(x: int, y: int) -> int:
    if y == 0:
        print('Division par 0')
    else:
        if x >= 0 and y >= 0:
            if x < y:
                return 0
            else:
                x = x - y
                return divEntier(x, y) + 1
        else:
            print('Nombre négatif')

if __name__ == '__main__':
    try:
        x = int(input('x : '))
        y = int(input('y : '))
    except ValueError:
        print('Entiers uniquement')
    else:
        print(divEntier(x, y))
