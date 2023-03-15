from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication, QLabel,QWidget,QGridLayout,\
    QLineEdit,QPushButton,QMainWindow,QTableWidget,QTableWidgetItem,\
    QDialog,QVBoxLayout,QComboBox,QToolBar,QStatusBar,QMessageBox
from PyQt6.QtGui import QAction,QIcon
import sys
# import sqlite3
import mysql.connector


# commit: refactoring: implemented mysql Sec48

# refactoring: update database class for mysql db connection
# note: ysql uses %s while sqlite need ? for placeholder in queries
# mysql user cursor.execute while sqlite uses conn.execute!!!
# cursor.execute(sql-query) and result=cursor.fetchall() # mysql specific, different from sqlite
class DatabaseConnection:
    def __init__(self,host='localhost',user='root',password='pythoncourse',database='school'):
        self.host=host
        self.user=user
        self.password=password
        self.database=database
    
    def connect(self):
        connection=mysql.connector.connect(host=self.host,user=self.user,
                                           password=self.password,database=self.database)
        return connection
    
       

# QMainWindow provides menu bar status bar and stuff!!!
class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle('Student Management System')
        self.setMinimumSize(450,400)

        # menu items
        file_menu_item=self.menuBar().addMenu('&File')
        edit_menu_item=self.menuBar().addMenu('&Edit')
        help_menu_item=self.menuBar().addMenu('&Help')

        add_student_action=QAction(QIcon('icons/add.png'),'Add Student',self)
        add_student_action.triggered.connect(self.insert) # mention the method to conncet it to 
        file_menu_item.addAction(add_student_action)

        about_action=QAction('About',self)
        help_menu_item.addAction(about_action)
        # about_action.setMenuRole(QAction.MenuRole.NoRole) # needed on mac if help menu is not shown!!!
        about_action.triggered.connect(self.about)

        search_action=QAction(QIcon('icons/search.png'),'Search',self)
        search_action.triggered.connect(self.search)
        edit_menu_item.addAction(search_action)

        self.table=QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(('Id','Name','Course','Mobile'))
        self.table.verticalHeader().setVisible(False) # hide the table id coumn!!!
        self.setCentralWidget(self.table)

        # create toolbar and toolbar elements
        toolbar=QToolBar()
        toolbar.setMovable(True) # movable tolbar!!!
        self.addToolBar(toolbar)
        toolbar.addAction(add_student_action)
        toolbar.addAction(search_action)

        # create status bar and add status bar elements
        self.statusbar=QStatusBar()
        self.setStatusBar(self.statusbar)
        # hello=QLabel('Hello there')
        # statusbar.addWidget(hello)

        # Detect a cell click
        self.table.cellClicked.connect(self.cell_clicked)


    def cell_clicked(self):
        edit_button=QPushButton('Edit Record')
        edit_button.clicked.connect(self.edit)

        delete_button=QPushButton('Delete Record')
        delete_button.clicked.connect(self.delete)

        children=self.findChildren(QPushButton)
        # print(children)
        if children:
            for child in children:
                self.statusbar.removeWidget(child)
                child.deleteLater() # dstroying the previous children

        self.statusbar.addWidget(edit_button)
        self.statusbar.addWidget(delete_button)


    def edit(self):
        dialog=EditDialog()
        dialog.exec()

    def delete(self):
        dialog=DeleteDialog()
        dialog.exec()

    def load_data(self):
        connection=DatabaseConnection().connect()
        cursor=connection.cursor() # mysql user cursor.execute while sqlite uses conn.execute!!!
        cursor.execute('SELECT * FROM students') # its a cursor obj!!!        
        result=cursor.fetchall() # mysql specific, different from sqlite
        self.table.setRowCount(0) # to reset the table so rows are not duplicated when resizing window etc.!!!
        for row_num,row_data in enumerate(result):
            self.table.insertRow(row_num)
            for colum_num,data in enumerate(row_data):
                # print(row_data)
                self.table.setItem(row_num,colum_num,QTableWidgetItem(str(data)))
        connection.close()

    def insert(self):
        dialog=InsertDialog() # another class we create
        dialog.exec()

    def search(self):
        dialog=SearchDialog()
        dialog.exec()

    def about(self):
        dialog=AboutDialog()
        dialog.exec()



class AboutDialog(QMessageBox):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('About')
        content='''
        This app was created during the course:
          "The Python Mega Course".
        Feel free to modify and reuse this app.
        '''
        self.setText(content)



class EditDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Update Student Data')
        self.setFixedWidth(300)
        self.setFixedHeight(300)
        layout=QVBoxLayout() # simple vertical layout

        # get student details from selected table row
        index=main_window.table.currentRow() # get selected row index
        student_name=main_window.table.item(index,1).text() # get row of table and 2nd col ie. name
        self.student_id=main_window.table.item(index,0).text() # get id from selected row
        course_name=main_window.table.item(index,2).text() # get course from selected row
        mobile=main_window.table.item(index,3).text() # get mobile from selected row

        # Add student name widget
        self.student_name=QLineEdit(student_name)
        self.student_name.setPlaceholderText('Name')
        layout.addWidget(self.student_name)

        # Add courses combobox
        self.course_name=QComboBox()
        courses=['Biology','Math','Astronomy','Physics']
        self.course_name.addItems(courses)
        self.course_name.setCurrentText(course_name) # set course got from the table
        layout.addWidget(self.course_name)

        # Add mobile Widget
        self.mobile=QLineEdit(mobile)
        self.mobile.setPlaceholderText('Name')
        layout.addWidget(self.mobile)

        # Add submit button
        button=QPushButton('Update')
        button.clicked.connect(self.update_student)
        layout.addWidget(button)

        self.setLayout(layout)

    def update_student(self):
        connection=DatabaseConnection().connect()
        cursor=connection.cursor()
        # mysql uses %s while sqlite need ? for placeholder in queries
        cursor.execute('UPDATE students SET name = %s, course = %s, mobile = %s WHERE id = %s',
                       (self.student_name.text(),
                        self.course_name.itemText(self.course_name.currentIndex()),
                        self.mobile.text(),
                        self.student_id))
        connection.commit()
        cursor.close()
        connection.close()

        # refresh table
        main_window.load_data() 

        # close edit window and show confirmation message
        self.close()
        confirm_widget=QMessageBox()
        confirm_widget.setWindowTitle('Success')
        confirm_widget.setText('This record was updated!')
        confirm_widget.exec()



class DeleteDialog(QDialog):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle('Delete Student Data')
        self.setFixedSize(300,100)
        layout=QGridLayout()
        confirmation=QLabel('Are you sure you want to delete?')
        yes=QPushButton('Yes')
        no=QPushButton('No')

        layout.addWidget(confirmation,0,0,1,2)
        layout.addWidget(yes,1,0)
        layout.addWidget(no,1,1)
        
        self.setLayout(layout)

        yes.clicked.connect(self.delete_student)
        no.clicked.connect(self.close_dialog)


    def delete_student(self):
        # get index and student id for selected table row
        index=main_window.table.currentRow()
        student_id=main_window.table.item(index,0).text()

        connection=DatabaseConnection().connect()
        cursor=connection.cursor()
        cursor.execute('DELETE from students WHERE id = %s',(student_id,))
        connection.commit()
        cursor.close()
        connection.close()
        main_window.load_data()

        self.close()

        # to show a simple notofocation dialog box
        confirmation_widget=QMessageBox() # this child of qdialog
        confirmation_widget.setWindowTitle('Success')
        confirmation_widget.setText('This record was deleted successfully!')
        confirmation_widget.exec()

    def close_dialog(self):
        self.close()



class InsertDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Insert Student Data')
        self.setFixedWidth(300)
        self.setFixedHeight(300)

        layout=QVBoxLayout() # simple vertical layout

        # Add student name widget
        self.student_name=QLineEdit()
        self.student_name.setPlaceholderText('Name')
        layout.addWidget(self.student_name)

        # Add courses combobox
        self.course_name=QComboBox()
        courses=['Biology','Math','Astronomy','Physics']
        self.course_name.addItems(courses)
        layout.addWidget(self.course_name)

        # Add mobile Widget
        self.mobile=QLineEdit()
        self.mobile.setPlaceholderText('Name')
        layout.addWidget(self.mobile)

        # Add submit button
        button=QPushButton('Register')
        button.clicked.connect(self.add_student)
        layout.addWidget(button)

        self.setLayout(layout)


    def add_student(self):
        name=self.student_name.text()
        course=self.course_name.itemText(self.course_name.currentIndex())
        mobile=self.mobile.text()
        connection=DatabaseConnection().connect()
        cursor=connection.cursor()
        cursor.execute('INSERT INTO students (name,course,mobile) VALUES (%s,%s,%s)',
                      (name,course,mobile))
        connection.commit()
        cursor.close()
        connection.close()
        main_window.load_data()



class SearchDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Search Student')
        self.setFixedSize(300,300)

        layout=QVBoxLayout()

        self.search_box=QLineEdit()
        self.search_box.setPlaceholderText('Name')
        layout.addWidget(self.search_box)

        button=QPushButton('Search')
        button.clicked.connect(self.search)
        layout.addWidget(button)

        self.setLayout(layout)

    def search(self):
        name=self.search_box.text()
        # print(f'Search: {name}')

        # connection=DatabaseConnection().connect()
        # cursor=connection.cursor()
        # cursor.execute('SELECT * FROM students WHERE name=%s',(name,))
        # result=cursor.fetchall()
        # rows=list(result)
        # print(rows)

        items=main_window.table.findItems(name,Qt.MatchFlag.MatchFixedString)
        for item in items:
            # print(item) # this is a table item object!!!
            # to set the name column as selected
            main_window.table.item(item.row(),1).setSelected(True)

        # cursor.close()
        # connection.close()



app=QApplication(sys.argv)
main_window=MainWindow()
main_window.show()
main_window.load_data()
sys.exit(app.exec())
