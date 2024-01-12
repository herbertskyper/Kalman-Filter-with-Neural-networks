class Mat:
    @staticmethod
    def check(mat1:'Mat', mat2:'Mat'):
        '''
        加减矩阵的时候检查行数列数是否相同
        '''
        if mat1.row != mat2.row or mat1.column != mat2.column:
            raise ValueError("矩阵的行数和列数必须相同")
        
    def inputMat(self):
        for i in range(self.row):
            for j, val in enumerate(map(int, input().split())):
                self.mat[i][j] = val

    def printMat(self):
        for i in range(self.row):
            for j in range(self.column):
                print(f"{self.mat[i][j]}", end=" ")
            print(" ")
        
    def __init__(self, row, column):# row 行
        self.mat = [[0] * column for _ in range(row)]
        self.row = row
        self.column = column

    def __add__(self, mat2):
        '''
        __add__是魔法方法，可以重载加号运算符（A+B的时候会被调用）
        '''
        Mat.check(self, mat2)
        retMat = Mat(self.row, self.column)
        for i in range(self.row):
            for j in range(self.column):
                retMat.mat[i][j] = self.mat[i][j]+mat2.mat[i][j]
        return retMat
    
    def __sub__(self, mat2):
        Mat.check(self, mat2)
        retMat = Mat(self.row, self.column)
        for i in range(self.row):
            for j in range(self.column):
                retMat.mat[i][j] = self.mat[i][j]-mat2.mat[i][j]
        return retMat
    
    def __mul__(self, mat2):
        Mat.check(self, mat2)
        retMat = Mat(self.row, mat2.column)
        for i in range(self.row):
            for j in range(mat2.column):
                sumVal=0
                for k in range(self.column):
                    sumVal += self.mat[i][k]*mat2.mat[k][j]
                retMat.mat[i][j] = sumVal

    def T(self):
        retMat = Mat(self.column, self.row)
        for i in range(self.row):
            for j in range(self.column):
                retMat.mat[j][i] = self.mat[i][j]
        self.row, self.column = self.column, self.row
        self.mat = retMat.mat
        return self

    # def inverse(self):
    #     retMat = Mat(self.row, self.column*2)
    #     for i in range(self.row):
    #         for j in range(self.column):

class SquareMat(Mat):
    def __init__(self, size):
        super().__init__(size, size)
        # super().inputMat()

    def swapRow(self, row1, row2):
        self.mat[row1], self.mat[row2] = self.mat[row2], self.mat[row1]

    def det(self):
        isNeg:bool = False

        for columnIndex in range(self.column):
            originalColumn = self.mat[columnIndex][columnIndex]

            if originalColumn==0:
                for rowIndex in range(columnIndex+1, self.row):
                    if self.mat[rowIndex][columnIndex]!=0:
                        self.swapRow(columnIndex, rowIndex)
                        isNeg = not isNeg
                        break

            else:
                for rowIndex in range(columnIndex+1, self.row):
                    if self.mat[rowIndex][columnIndex]==0:
                        continue
                    else:
                        ratio:float = self.mat[rowIndex][columnIndex]/originalColumn
                        for i in range(columnIndex, self.column):
                            self.mat[rowIndex][i] -= ratio*self.mat[columnIndex][i]

        detVal = 1 if not isNeg else -1
        for i in range(self.row):
            detVal *= self.mat[i][i]

        return detVal
    
    def childDet(self, r, c):
        mat2 = SquareMat(self.row-1)
        for i in range(self.row):
            for j in range(self.column):
                if i<r and j<c:
                    mat2.mat[i][j] = self.mat[i][j]
                elif i<r and j>c:
                    mat2.mat[i][j-1] = self.mat[i][j]
                elif i>r and j<c:
                    mat2.mat[i-1][j] = self.mat[i][j]
                elif i>r and j>c:
                    mat2.mat[i-1][j-1] = self.mat[i][j]
        return mat2.det()
    
    def inv(self):
        detVal = self.det()
        if detVal==0:
            print("Cannot find inverse of this matrix")
            return

        matStar = SquareMat(self.row)
        for i in range(self.row):
            for j in range(self.column):
                element = self.childDet(i,j)*(-1)**(i+j)
                matStar.mat[i][j] = element/detVal
        return matStar.T()
                    


# a1,a2,b1,b2 = list(map(int,input("Please input the size of the two Matrixes\nand each of the element\n").split()))
# A = Mat(a1,a2)
# B = Mat(b1,b2)
# A.inputMat()
# B.inputMat()
# C = A-B
# C.printMat()
D = SquareMat(2)
D.inputMat()
print(D.det())
D.inv().printMat()