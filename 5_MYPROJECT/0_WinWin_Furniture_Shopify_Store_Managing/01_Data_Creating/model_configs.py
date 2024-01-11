import pandas as pd
import numpy as np
from datetime import datetime
import pickle
import os.path

import gspread
from gspread_dataframe import set_with_dataframe
from google.oauth2.service_account import Credentials
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive

from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

import warnings
warnings.filterwarnings("ignore")
warnings.warn("this will not show")

"""
This file includes the common elements used in the model
"""

Vendor_Dict = {"Ashley" : "11rM_IdQgTp-C4OAby2FjA3jCF3kmQcrMl2NfliySeMQ",
              "Bellona" : "1tk7zeUWyqSckbe7QlCIoMwupz3wkps7NyDZy2Zdc6Lg",
              "Beyan" : "13h3mS2zCL_hkOC4P0pQTvjhPa7Z95t0lR6o8rDN1HBE",
              "Casamode" : "1CpRiANh-Bu0zJfZ2Y4EFLoGAJBExFtWrznACEeRzYDU",
              "Coaster" : "1SXuwwYXMWaUXDuwKe_uIaNN8OumGMwoyDjhjbfv19PM",
              "Corsicana" : "1wEWOO1hZtkaMnKoKswKyi1_dWs4hE4PV4SfSd0_strw",
              "Cosmos" : "1lryk9YFXmEjmAhSAJhHZgDm7WjBncQKirkJ291dzYsI",
              "Crown_Mark" : "1uL39iYxNWcjsHHiq9dcMD4q7wr5etM2mmWlZpmJ_hu0",
              "Donco_Kids" : "1m-UXoA0hMQgdQC7i5kZieGWiYWkuITqBZqpSEi5QzUI",
              "Empire" : "1wqMMvNcRWl-0ym_Bn6PR5Deu-0CvhgllrLsBn9QH1nw",
              "Furniture_of_America" : "1wdNt0oPuZVgtLyN6zA9LwRQQvipLF1Tj6vmsFj0FFMA",
              "Furniture_World" : "1s5CImHPUm5H1O48a0p_e4Ph5YWYPnXT6CNRV_fYXKpU",
              "Galaxy" : "1p6wkUt8baI8BAVbg7n6qa2Ct-wh1v4aZeWyd5hG53RM",
              "Global_Furniture" : "1MGYKdxPbVMrEtaL_reSplUqXnh_jzNHnmJtpZV2k4cM",
              "Glory" : "1BUSuq_R5zYrN0JlG0JTM4w5B0mCO96kycfgpdHAue8g",
              "Happy_Homes" : "1g9ut7lXhDiD9yeW9-h_81SEsres9cPfqcTKxcACfA6Q",
              "Hollywood" : "1MWW03HImx_ZjUnSrYaD1ae09ImW1gNBkdwc_oDHchz8",
              "Homelegance" : "129PWgvIp4qE56r-1--0ntuGwxnS0kCkl591jcV8mcV8",
              "Lidixh" : "1GtdxvH03AfjqcrknDxVB966CIYrRWP1V2MsYID3cpLU",
              "Mainline" : "1qPewlXYGcJDLUpdzDFfLRjriMUO9HLyE6rGHJv96iwo",
              "Meridian" : "1Pzb9kcgd3_FT3iLsB0yVAkyBGL2kNQj3OwPhEjS_SAU",
              "New_Art" : "1KpgUz0VU3NnSmHGhWKimpNFu1b5o2atqmTZyxP49Mrg",
              "New_Classic" : "17ZG-sQDOn7V4UbmoWl4caStytimdaeL5TSM074y7SYQ",
              "New_York_Diamond" : "1y2rwb9529J1u0Zgqn-nYacjw9gdVM0ezaM4fcI-hxJQ",
              "Nova" : "19cu7_yFO7LWdA5XvfhxLdjeQzy6nKpmfpmSq4oDjYZ0"}   

Created_Dict = {"OrdersAll" : "1CTJoUGb-6hYMinjxw6k1W7YfCHMjI58JoFLx1j2ST8Q",
                "Invoice" : "1xpSh6Oe3JmhLHw6k7s1c0Xz9NWHsvdw3Qn5pK-iqfdA",
                "Orders" : "1b7zpEQhPiD9rnqANM_xVxMynaKW9RsAVP4idYsjDVos",
                "SKU" : "1hOLVEEWgy3PnHdjb-GMyEzaJW4RTK6UUk14gjAKxNv0",
                "Balance" : "1XfEaGblkghoEDYtyuc_bos4jQdmq7_EpGXyP0AA-woI",
                "Stock" : "1OfqUs7-tQ_K1SqSj2yJS5l1YWodPrh8smg9Q1InZ18c",
                "Cost" : "1A1ZKI0gDW_nbpS9UUtnbdbEyVJ6o_GQ4Dwn8pJaj-sQ",
                "OsmanStock" : "1gMTa-cwBrWIFfmhPJJQc1kiVZ2gfVgBgNts05OhYzH4",
                "Shopify" : "19QuYb1iEFf7Op-llo3N0qJFtIHg2A_tXXI8gAnJjlgo",
                "Monthly" : "1I3MGrtcE7SVsbq5k8WSNYw6eyBu5bjQ046Cop20f9DE"}        

Gap_Dict = {"OrdersAll" : "All!A1:Z10000",
             "Invoice" : "Invoice!A2:I10000",
             "Orders" : "Orders!A1:H10000",
             "SKU" : "SKU!A1:D10000",
             "Balance" : "Balance!A1:N10000",
             "Stock" : "Stock!A1:H10000",
             "Cost" : "Cost!A2:L10000",
             "Osman_Stock" : "Osman_Stock!A2:M10000",
             "Shopify" : "Shopify!A1:I10000",
             "Monthly" : "Monthly!A1:N100"}

Vendor_List = list(Vendor_Dict.keys())
Pull_Key_List = list(Vendor_Dict.values())

Created_List = list(Created_Dict.keys())
Created_Key_List = list(Created_Dict.values())

Sheet_List = list(Gap_Dict.keys())
Sheet_Gap_List = list(Gap_Dict.values())

folder_path = os.getcwd()
client_path = os.path.join(folder_path, "client_secrets.json")
client_path1 = os.path.join(folder_path, "client_secrets1.json")
token_path = os.path.join(folder_path, "token.pickle")

scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
credentials = Credentials.from_service_account_file(client_path1, scopes=scopes)

# Connect Google Drive
def Connect_Drive (CREDENTIALS):
    gc = gspread.authorize(CREDENTIALS)
    gauth = GoogleAuth()
    drive = GoogleDrive(gauth)

# Create Google Sheet
def Created_Sheet (CREDENTIALS, CREATED_KEY_LIST, CREATED_LIST):
    gs = gspread.authorize(credentials=CREDENTIALS).open_by_key(CREATED_KEY_LIST)
    ws = gs.worksheet(CREATED_LIST)

# Google API Check Function
def Gsheet_Api_Check(SCOPES):
    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(client_path, SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    return creds

# Google Sheet Data Pull Function
def Pull_Sheet_Data(SCOPES, SHEET_LIST, SHEET_GAP_LIST):
    creds = Gsheet_Api_Check(SCOPES)
    service = build("sheets", "v4", credentials=creds)
    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId=SHEET_LIST, range=SHEET_GAP_LIST).execute()
    values = result.get("values", [])
    
    if not values:
        print("No data found.")
    else:
        rows = sheet.values().get(spreadsheetId=SHEET_LIST, range=SHEET_GAP_LIST).execute()
        data = rows.get("values")
        #print("COMPLETE: Data copied")
        return data

# Create All Gsheets to One Gsheet
def Create_All_Gsheets (SHEET_GAP_LIST, CREATED_KEY_LIST, CREATED_LIST, VENDOR_LIST, PULL_KEY_LIST, CREDENTIALS):
    i = 0
    for data_gap in SHEET_GAP_LIST:
        gs = gspread.authorize(credentials=CREDENTIALS).open_by_key(CREATED_KEY_LIST[i])
        ws = gs.worksheet(CREATED_LIST[i])
        print(f"{Sheet_List[i]} Started:")  
        df_all = pd.DataFrame()
        j = 0
        for order_key in PULL_KEY_LIST:
            vendor = VENDOR_LIST[j]
            data = Pull_Sheet_Data(scopes, order_key, data_gap)
            df = pd.DataFrame(data[1:], columns=data[0])
            a = list(df.columns).index('Vendor')
            df = df.iloc[:df.iloc[:,a].replace("", np.nan).count()]
            print(f"{Sheet_List[i]}-{vendor} Copied & Shape: {df.shape}")  
            df_all = pd.concat([df_all, df])
            j +=1
        print(f"All {Sheet_List[i]} Copied & Shape: {df_all.shape}")
        df = df_all
        df.dropna(axis=0,how="all",inplace=True)

        ws.clear()
        set_with_dataframe(worksheet=ws, dataframe=df, include_index=False, include_column_header=True, resize=True) 
        i +=1

# Create Orders Gsheets to One Gsheet
def Create_Orders (CREATED_KEY_LIST, CREATED_LIST, INDEX, SHEET_GAP_LIST, VENDOR_LIST, PULL_KEY_LIST, CREDENTIALS):
    gs = gspread.authorize(credentials=CREDENTIALS).open_by_key(CREATED_KEY_LIST[INDEX])
    ws = gs.worksheet(CREATED_LIST[INDEX]) 
    df_all = pd.DataFrame()
    i = 0
    print(f"{Sheet_List[INDEX]} Started:")
    for pull_key in PULL_KEY_LIST:
        vendor = VENDOR_LIST[i]
        data = Pull_Sheet_Data(scopes, pull_key, SHEET_GAP_LIST[INDEX])
        df = pd.DataFrame(data[1:], columns=data[0])
        a = list(df.columns).index('Vendor')
        df = df.iloc[:df.iloc[:,a].replace("", np.nan).count()]
        print(f"{vendor} Copied & Shape: {df.shape}")  
        df_all = pd.concat([df_all, df])
        i +=1
    print(f"{Sheet_List[INDEX]} Finished & Shape: {df_all.shape}")
    df = df_all
    df.dropna(axis=0,how="all",inplace=True)
    ws.clear()
    set_with_dataframe(worksheet=ws, dataframe=df, include_index=False, include_column_header=True, resize=True)  

# Create Monthly Gsheets to One Gsheet
def Create_Monthly (CREATED_KEY_LIST, CREATED_LIST, INDEX, SHEET_GAP_LIST, VENDOR_LIST, PULL_KEY_LIST, CREDENTIALS):
    gs = gspread.authorize(credentials=CREDENTIALS).open_by_key(CREATED_KEY_LIST[INDEX])
    ws = gs.worksheet(CREATED_LIST[INDEX]) 
    df_all = pd.DataFrame()
    i = 0
    print(f"{Sheet_List[INDEX]} Started:")
    for pull_key in PULL_KEY_LIST:
        vendor = VENDOR_LIST[i]
        data = Pull_Sheet_Data(scopes, pull_key, SHEET_GAP_LIST[INDEX])
        df = pd.DataFrame(data[1:], columns=data[0])
        print(f"{vendor} Copied & Shape: {df.shape}")  
        df_all = pd.concat([df_all, df])
        i +=1
    print(f"{Sheet_List[INDEX]} Finished & Shape: {df_all.shape}")
    df = df_all
    df.dropna(axis=0,how="all",inplace=True)
    df = df.iloc[1:,0:][: :2]    
    ws.clear()
    set_with_dataframe(worksheet=ws, dataframe=df, include_index=False, include_column_header=True, resize=True)
