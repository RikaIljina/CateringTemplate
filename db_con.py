import streamlit as st
from streamlit_gsheets import GSheetsConnection
import gspread
import time
# from oauthlib.oauth2 import ServiceAccountCredentials
# scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']

from gspread_formatting import CellFormat, Color, TextFormat, format_cell_range, format_cell_ranges, set_row_height

class CatSheet():
    def __init__(self):
        # gc = gspread.service_account(filename="service_account.json")
        # sh = gc.open("Catering offert mall")
        #sh.append_row(["name"])
        self.conn = st.connection("gsheets", type=GSheetsConnection)

    def read(self, name, cols):
       # return self.conn.worksheet(name).col_values(cols)
        return self.conn.read(worksheet=name, usecols=list(range(cols)), ttl=10)

    def write(self, name, dff):
        df = self.conn.update(
            worksheet=name,
            data=[[dff]],
            
        )
        print(df)

    def write_result(self, df):
        dff = self.conn.update(
            worksheet="Resultat",
            data=df,
        )
        print("result:", dff)

class UpdSheet():
    def __init__(self):
        print("Connecting with gspread...")
        self.gc = gspread.service_account(filename="service_account.json")
        self.conn = self.gc.open("Catering offert mall")

    def create(self):
        new_sheet = self.gc.create("Catering_test")
        new_sheet.share('wasirika@gmail.com', perm_type='user', role='writer')
        return new_sheet.url


    def write(self, name, data, pos):
        st.write(pos)
        print("Writing with gspread...")

        # self.conn.worksheet(name).update_cell(pos + 2, 1, data)
        if isinstance(data, str):
            self.conn.worksheet(name).update(f"A{pos + 2}", [[data]])
        else:
            self.conn.worksheet(name).update(f"A{pos + 2}", [data])

    def write_range(self, name, data):
        print("##### batch : ",self.conn.worksheet(name).batch_update(data)) # update(range, [data])

    def read(self):
        return self.conn.worksheet("Resultat").get_all_values()

    def merge_cells(self, range, daytime_headers):
        # self.conn.worksheet("Resultat").merge_cells(range, merge_type=("MergeType.MERGE_COLUMNS"))
        range.extend(daytime_headers)
        print(" BBBUG", daytime_headers)
        print(" #### BBUG", range)
        for el in range:
            print("merging: ", el)
            self.conn.worksheet("Resultat").merge_cells(f"A{el[1:]}:B{el[1:]}")

        set_row_height(self.conn.worksheet("Resultat"), "1:2", 75)
   

       # print(self.conn.worksheet("Resultat").merge_cells(f"A11:B11"))
        
        #set_row_height(self.conn.worksheet("Resultat"), "1:5", 75)
            #time.sleep(10)
        # fmt = CellFormat(
        # backgroundColor=Color(1, 0.9, 0.9),
        # textFormat=TextFormat(bold=True, foregroundColor=Color(0, 0, 0)),
        # horizontalAlignment='CENTER'
        # )

      #  format_cell_range(self.conn.worksheet("Resultat"), 'A9', fmt)

    def center_text(self, headers, daytime_headers, special_rows):
        fmt_bold = CellFormat(
            textFormat=TextFormat(bold=True, foregroundColor=Color(0, 0, 0), fontFamily="Calibri", fontSize=11),
            horizontalAlignment='LEFT',
            wrapStrategy="WRAP",
        )

        fmt_not_bold = CellFormat(
            textFormat=TextFormat(bold=False, foregroundColor=Color(0, 0, 0), fontFamily="Calibri", fontSize=11),
            horizontalAlignment='LEFT',
            wrapStrategy="WRAP",
        )

        fmt_title = CellFormat(
#        backgroundColor=Color(1, 0.9, 0.9),
        textFormat=TextFormat(bold=True, foregroundColor=Color(0, 0, 0), fontFamily="Calibri", fontSize=16),
        backgroundColor=Color(0.878, 0.878, 0.878),
        horizontalAlignment='CENTER',
        verticalAlignment='MIDDLE',
        wrapStrategy="WRAP",
        )

        fmt_subtitle = CellFormat(
#        backgroundColor=Color(1, 0.9, 0.9),
        textFormat=TextFormat(bold=True, foregroundColor=Color(0, 0, 0), fontFamily="Calibri", fontSize=12),
        backgroundColor=Color(0.878, 0.878, 0.878),
        horizontalAlignment='CENTER',
        verticalAlignment='MIDDLE',
        wrapStrategy="WRAP",
        )

        fmt_dt = CellFormat(textFormat=TextFormat(bold=True, foregroundColor=Color(0, 0, 0), fontFamily="Calibri", fontSize=12),
        backgroundColor=Color(0.855, 0.914, 0.969),
        horizontalAlignment='CENTER',
        wrapStrategy="WRAP",
        )

        fmt_sp = CellFormat(textFormat=TextFormat(bold=True, foregroundColor=Color(0, 0, 0), fontFamily="Calibri", fontSize=11),
        backgroundColor=Color(0.851, 0.949, 0.816),
        horizontalAlignment='LEFT',
        wrapStrategy="WRAP",
        )

        format_range = [("A:A", fmt_bold), ("B:B", fmt_not_bold)]
        
        #for el in headers:
            #print("centering:", el)
        format_range.append((headers[0], fmt_title))
        format_range.append((headers[1], fmt_subtitle))

        for dt_h in daytime_headers:
            format_range.append((dt_h, fmt_dt))
        for sp in special_rows:
            format_range.append((sp, fmt_sp))

        # format_cell_range(self.conn.worksheet("Resultat"), range, fmt) # format_cell_ranges(worksheet, [('A1:J1', fmt), ('K1:K200', fmt2)]) !!!
        format_cell_ranges(self.conn.worksheet("Resultat"), format_range)
        self.conn.worksheet("Resultat").rows_auto_resize(3, 30)


        # self.conn.worksheet("Resultat").merge_cells(range, merge_type='MERGE_COLUMNS')

# To clear cache  and rerun app:
        # st.cache_data.clear()
        # st.rerun()

        # update connection class
 # 