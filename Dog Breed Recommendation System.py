from shiny import App, render, ui, reactive
import psycopg2
import pandas as pd
import asyncio
from plotnine import *
import folium
from folium.plugins import MarkerCluster
from folium import Marker
import psycopg2
import pandas as pd
import webbrowser
from urllib.request import urlopen
from PIL import Image
from io import BytesIO
import requests





connection_info = "host=147.47.200.145 dbname=teamdb8 user=team8 password=petproject8 port=34543"
conn = psycopg2.connect(connection_info)
cur = conn.cursor()
dog_breed= pd.read_sql("SELECT * FROM dog_breed", conn)
vet = pd.read_sql("SELECT * FROM vet_clinic", conn)
group= pd.read_sql("SELECT * from dog_group", conn)

cur.close()
conn.close()
        

hound= dog_breed.query('breed_group=="Hound "')
toy= dog_breed.query('breed_group=="Toy "')
terrier= dog_breed.query('breed_group=="Terrier "')
working= dog_breed.query('breed_group=="Working "')
herding= dog_breed.query('breed_group== "Herding "')
foundation= dog_breed.query('breed_group=="Foundation Stock Service"')
non_sporting= dog_breed.query('breed_group=="Non-Sporting "')
sporting= dog_breed.query('breed_group== "Sporting"')
misc= dog_breed.query('breed_group=="Miscellaneous Class"')




class Map:
    
    def showMap(self):
        #Create the map
        m = folium.Map(location=[vet['위도'][0], vet['경도'][0]],  # location : 임시로 경위도 지정.
               zoom_start=13,  # 지도 배율 조정
               width=750,  # 지도크기 조절
               height=500   # 지도크기 조절
              )
        
        for i in range(len(vet)):
            popup_i = "'<pre>" + str(vet['영업시간'][i]) + "</pre><pre>"+ str(vet['review_1'][i]) + "</pre><pre>"+ str(vet['review_2'][i])+"</pre><pre>" + str(vet['review_3'][i])+"</pre>'"
            folium.Marker([vet['위도'][i], vet['경도'][i]],
                        popup = popup_i,
                        tooltip = vet['사업장명'][i]).add_to(m)

        #Display the map
        m.save("m.html")
        webbrowser.open("m.html")



def choose_group(df, hound, toy, terrier,working, herding, foundation, non_sporting, sporting, misc):
  if df['breed_group'].iloc[0]== "Hound ":
    return hound
  if df['breed_group'].iloc[0]== "Toy ":
    return toy
  if df['breed_group'].iloc[0]== "Terrier ":
    return terrier
  if df['breed_group'].iloc[0]== "Working ":
    return working
  if df['breed_group'].iloc[0]== "Herding ":
    return herding
  if df['breed_group'].iloc[0]== "Foundation Stock Service":
    return foundation
  if df['breed_group'].iloc[0]== "Non-Sporting ":
    return non_sporting
  if df['breed_group'].iloc[0]== "Sporting":
    return sporting
  if df['breed_group'].iloc[0]== "Miscellaneous Class":
    return misc

def ifelse (df, x, res1, res2):
            if x == df:
                res = res1
            else:
                res= res2
            return(res)

app_ui = ui.page_fluid(
    ui.panel_title("Dog Breed Recommendation System"),
    ui.navset_tab_card(
        ui.nav("Sign Up",
            ui.layout_sidebar(
                ui.panel_sidebar(
                    ui.input_text("username", "Enter Username", placeholder="Enter Username"),
                    ui.input_password("password", "Enter Password", placeholder="Enter Password"),
                    
                    ui.input_checkbox("adopt", "Are not you not here to adopt?", False),
                    ui.panel_conditional(
                        "input.adopt",
                        ui.input_text("user_breed","Enter Your Dog's Breed", placeholder="eg) Bulldog")

                    ),
                    ui.input_action_button("signup", "Sign Up"),
                    ui.output_text("signup"),
                    
                ),
                ui.panel_main(
                    ui.panel_conditional(
                        "input.adopt",
                        ui.output_text("general_info_header_user"),
                        ui.output_table("info_user"),
                        ui.output_text("health_header_user"),
                        ui.output_table("health_user"),
                        ui.output_plot("plot_user"),
                        ui.output_plot("height_plot_user"),
                        ui.output_plot("weight_plot_user"),
                        ui.output_plot("life_expect_plot_user"),
                        ui.output_plot("cmd_plot_user"),
                        ui.output_plot("ltc_plot_user"),

                    ),
                    
                    ),
                ),
            ),
        ui.nav("Filter Dog Breeds", 
            ui.layout_sidebar(
                ui.panel_sidebar(
                    ui.input_text("username", "Enter Username", placeholder="Enter Username"),
                    "Question 1) \nDo you have kids under the age of 10?",
                    ui.input_checkbox("q1", "Yes"),
                    "Question 2) \nAre you new to raising dogs?",
                    ui.input_checkbox("q2", "Yes"),
                    "Question 3) How energetic are you? (1:lowest, 5: highest)",
                    ui.input_slider("q3","", min=0, max=5, value=3),
                    "Question 4) Does grooming frequency matter for you?",
                    ui.input_checkbox("q4", "Yes, I don’t have a lot of time to groom"),
                    "Question 5) What is your home like?",
                    ui.input_select("q5", "", {"a": "An apartment", "b": "A house with a small yard", "c": "A house with a large yard"}),
                    
                    # Additional Options
                    ui.input_checkbox("show", "Additional Options:", False),
                    ui.panel_conditional(
                        "input.show", ui.input_radio_buttons("options", "", ["Filter Rows", "Sort by Column"])
                    ),
                    ui.panel_conditional(
                        "input.show && input.options === 'Filter Rows'",
                        ui.input_numeric("row", "How many breeds do you want to see at once?", value=100),
                    ),
                    ui.panel_conditional(
                        "input.show && input.options === 'Sort by Column'",
                        ui.input_select("filter", "Filter by", {"breed": "Breed", "breed_group": "Breed Group","size_cat": "Size Category", "groom_cat": "Grooming", "shedding_cat": "Shedding", "energy_level_cat":"Energy Level", "demeanor_cat":"Demeanor", "trainability_cat": "Trainability"}),
                    ),

                    # Search Button
                    ui.input_action_button("search", "Search"),
                    ui.output_text("button"),
                    ui.output_text("user_info_save"),
                ),
                ui.panel_main(
                    ui.output_table("a_df"),
                ),
            ),
        ),
        ui.nav("Dog Breed Traits", 
            ui.layout_sidebar(
                ui.panel_sidebar(
                    ui.input_text("breed", "Input Breed Name", placeholder="e.g) Bulldog"),
                    ui.input_action_button("search2", "Search"),
                    ui.output_text("plotting"),
                ),
                ui.panel_main(
                    ui.output_table("info"),
                    ui.output_text("lmaoxd"),
                    ui.output_text("lmaoxd1"),
                    ui.output_text("lmaoxd2"),
                    ui.output_text("health_header"),
                    ui.output_table("health"),
                    ui.output_plot("plot"),
                    ui.output_plot("height_plot"),
                    ui.output_plot("weight_plot"),
                    ui.output_plot("life_expect_plot"),
                    ui.output_plot("cmd_plot"),
                    ui.output_plot("ltc_plot"),
                    ),
                ),
            ),
        ui.nav("Hospitals", 
            ui.layout_sidebar(
                ui.panel_sidebar(
                    ui.input_action_button("hospitals", "Search Nearest Hospitals"),
                ),
                ui.panel_main(
                    ui.output_text("map"),
                    ),
                ),
            ),
        ),
        
)




def server(input, output, session):
    @reactive.Calc
    def questionnaire():
        if input.q1():
            kid= 2
        else:
            kid= 3
        if input.q2():
            exp= 0.6
        else:
            exp= 0
        energy= input.q3()
        if input.q4():
            groom=0.4
        else:
            groom=1
        if input.q5()== "An apartment":
            size= 'medium'
        else:
            size= 'large'
        return kid, exp, energy, groom, size

        

    @output
    @render.table
    @reactive.event(input.search)
    async def a_df():
        conn = psycopg2.connect(connection_info)

        cur = conn.cursor()

        user_dog= pd.read_sql("SELECT breed, breed_group, size_cat, groom_cat, shedding_cat, energy_level_cat, demeanor_cat, trainability_cat, temperament1, temperament2, temperament3  FROM dog_breed WHERE child <= %s AND trainability_value>= %s AND energy_level_value*5 <= %s AND groom_value<=%s AND (size_cat= 'small' OR size_cat= 'medium' or size_cat=%s)", conn, params=questionnaire())    


        cur.close()
        conn.close()
        
        await asyncio.sleep(1)
        user_dog= user_dog[['breed','breed_group','size_cat','groom_cat','shedding_cat','energy_level_cat','demeanor_cat','trainability_cat','temperament1','temperament2','temperament3']].head(input.row())
        return user_dog.sort_values(by=[input.filter()])
    
    @output
    @render.text
    @reactive.event(input.search)
    def user_info_save():
        conn = psycopg2.connect(connection_info)
        try:
        
            cur = conn.cursor()
            # 값 변경 쿼리
            cur.execute("UPDATE users set has_kids=%s, has_exp=%s, energy_level=%s, groom_freq=%s, home=%s where username=%s",(input.q1(),input.q2(),input.q3(),input.q4(),input.q5(),input.username()))
            
            # 트랜잭션 커밋 - 데이터베이스에 업데이트를 반영
            conn.commit()


        except psycopg2.Error as e:
            # 데이터베이스 에러 처리
            print("DB error: ", e)
            # 롤백- 최근 커밋 이후의 transaction들을 모두 취소
            conn.rollback()
            

        finally:
            cur.close()
            conn.close()

                
        return "Added to User Info"
        
    @output
    @render.text
    @reactive.event(input.search)
    async def button():
        #Additional mechanism for Searching
        with ui.Progress(min=1, max=15) as p:
            p.set(message="Searching in progress", detail="This may take a while...")

            for i in range(1, 15):
                p.set(i, message="Searching")
                await asyncio.sleep(0.1)
        return "Done Searching!"

    @output
    @render.text
    @reactive.event(input.search2)
    async def plotting():
        #Additional mechanism for Searching
        with ui.Progress(min=1, max=15) as p:
            p.set(message="Plotting in progress", detail="This may take a while...")

            for i in range(1, 15):
                p.set(i, message="Plotting")
                await asyncio.sleep(0.1)
        return "Done Plotting!"

    @output
    @render.plot()
    @reactive.event(input.search2)
    async def plot():
        await asyncio.sleep(0.1)
        dog_choice= input.breed()
        df= dog_breed.query('breed==@dog_choice')
        a=(ggplot(dog_breed)
        #groom value
        +geom_linerange(aes(ymin="0", ymax= "1", x=0.5),color="#3FCBAB",size=4)
        +geom_text(x= 0.5, y=-0.22, label="Grooming frequency",size= 9)
        +geom_text(x= 0.55, y=0.5, label=df['groom_cat'].iloc[0], size=9)
        +coord_flip()
        +geom_point(df, y= df['groom_value'].iloc[0], x=0.5, color='grey', size=3)
        #shedding value
        +geom_linerange(aes(ymin="0", ymax= "1", x=0.4),color="#3FCBAB",size=4)
        +geom_text(x= 0.4, y=-0.22, label="Shedding frequency",size= 9)
        +geom_text(x= 0.45, y=0.5, label=df['shedding_cat'].iloc[0], size=9)
        +coord_flip()
        +geom_point(df, y= df['shedding_value'].iloc[0], x=0.4, color='grey', size=3)
        #energy level value
        +geom_linerange(aes(ymin="0", ymax= "1", x=0.3),color="#3FCBAB",size=4)
        +geom_text(x= 0.3, y=-0.22, label="Energy Level",size= 9)
        +geom_text(x= 0.35, y=0.5, label=df['energy_level_cat'].iloc[0], size=9)
        +coord_flip()
        +geom_point(df, y= df['energy_level_value'].iloc[0], x=0.3, color='grey', size=3)
        #demeanor value
        +geom_linerange(aes(ymin="0", ymax= "1", x=0.2),color="#3FCBAB",size=4)
        +geom_text(x= 0.2, y=-0.22, label="Demeanor Value",size= 9)
        +geom_text(x= 0.25, y=0.5, label=df['demeanor_cat'].iloc[0], size=9)
        +coord_flip()
        +geom_point(df, y= df['demeanor_value'].iloc[0], x=0.2, color='grey', size=3)
        #trainability value
        +geom_linerange(aes(ymin="0", ymax= "1", x=0.1),color="#3FCBAB",size=4)
        +geom_text(x= 0.1, y=-0.22, label="Trainability",size= 9)
        +geom_text(x= 0.15, y=0.5, label=df['trainability_cat'].iloc[0], size=9)
        +coord_flip()
        +geom_point(df, y= df['trainability_value'].iloc[0], x=0.1, color='grey', size=3)
        #axis
        +ylim(-0.4,1)
        +xlim(0.08,0.55)
        +labs(x=("Traits of "+ df['breed'].iloc[0])))        
        return a

    @output
    @render.plot()
    @reactive.event(input.search2)
    async def life_expect_plot():
        dog_choice= input.breed()
        df= dog_breed.query('breed==@dog_choice')
        df= choose_group(df, hound, toy, terrier, working, herding, foundation, non_sporting, sporting, misc)
        df['chosen'] = df['breed'].apply(lambda x: ifelse(x, dog_choice, "Yes", "No"))
        b=(ggplot(df, aes(x="reorder(breed, (min_expectancy+max_expectancy)/2)", y= "(min_expectancy+max_expectancy)/2"))
        + geom_linerange(aes(ymin='min_expectancy', ymax= "max_expectancy", color="chosen"),size=2)
        + geom_point(color = "black", size= 0.5, alpha= 0.3)
        + coord_flip()
        + scale_colour_manual(values = ("#D8D0CF", "#3FCBAB"))
        + theme(legend_position='none')
        + labs(x="Breed", y="Life Expectancy Range(years)"))
        return b


    @output
    @render.plot()
    @reactive.event(input.search2)
    async def weight_plot():
        dog_choice= input.breed()
        df= dog_breed.query('breed==@dog_choice')
        df= choose_group(df, hound, toy, terrier, working, herding, foundation, non_sporting, sporting, misc)
        df['chosen'] = df['breed'].apply(lambda x: ifelse(x, dog_choice, "Yes", "No"))
        c=(ggplot(df, aes(x="reorder(breed, (min_weight+max_weight)/2)", y= "(min_weight+max_weight)/2"))
        + geom_linerange(aes(ymin="min_weight", ymax= "max_weight", color="chosen"),size=2)
        + geom_point(color="black", size= 0.5,alpha=0.3)
        + coord_flip()
        + scale_colour_manual(values = ("#D8D0CF", "#3FCBAB"))
        + theme(legend_position='none')
        + labs(x="Breed", y="Weight Range(kg)"))
        return c

    @output
    @render.text()
    @reactive.event(input.search2)
    async def lmaoxd():
        return "Breeds in the Working Group are dogkind's punch-the-clock, blue-collar workers, and the group includes some of the world's most ancient breeds. They were developed to assist humans, including pulling sleds and carts, guarding flocks and homes, and protecting their families. Breeds in the Working Group tend to be known for imposing stature, strength, and intelligence."

    @output
    @render.text()
    @reactive.event(input.search2)
    async def lmaoxd1():
        return "Other Breeds in Group: Working"

    @output
    @render.text()
    @reactive.event(input.search2)
    async def lmaoxd2():
        return "Boxer, Great Dane, Rottweiler"

    @output
    @render.plot()
    @reactive.event(input.search2)
    async def height_plot():
        dog_choice= input.breed()
        df= dog_breed.query('breed==@dog_choice')
        df= choose_group(df, hound, toy, terrier, working, herding, foundation, non_sporting, sporting, misc)
        df['chosen'] = df['breed'].apply(lambda x: ifelse(x, dog_choice, "Yes", "No"))
        d=(ggplot(df, aes(x="reorder(breed, (min_height+max_height)/2)", y= "(min_height+max_height)/2"))
        + geom_linerange(aes(ymin="min_height", ymax= "max_height", color="chosen"),size=2)
        + geom_point(color="black", size= 0.5,alpha =0.3)
        + coord_flip()
        + scale_colour_manual(values = ("#D8D0CF", "#3FCBAB"))
        + theme(legend_position='none')
        + labs(x="Breed", y="Height Range(cm)"))
        return d

    @output
    @render.plot()
    @reactive.event(input.search2)
    async def cmd_plot():
        dog_choice= input.breed()
        df= dog_breed.query('breed==@dog_choice')
        df= choose_group(df, hound, toy, terrier, working, herding, foundation, non_sporting, sporting, misc)
        df['chosen'] = df['breed'].apply(lambda x: ifelse(x, dog_choice, "Yes", "No"))
        e=(ggplot(choose_group(df, hound, toy, terrier,working, herding, foundation, non_sporting, sporting, misc), aes(x="reorder(breed, (comm_min+comm_max)/2)", y= "(comm_min+comm_max)/2"))
        + geom_linerange(aes(ymin="comm_min", ymax= "comm_max", color="chosen"),size=2)
        + geom_point(color="black", size= 0.5,alpha=0.3)
        + coord_flip()
        + scale_colour_manual(values = ("#D8D0CF", "#3FCBAB"))
        + theme(legend_position='none')
        + labs(x="Breed", y="Repetitions to understand new command"))
        return e


    @output
    @render.plot()
    @reactive.event(input.search2)
    async def ltc_plot():
        dog_choice= input.breed()
        df= dog_breed.query('breed==@dog_choice')
        df= choose_group(df, hound, toy, terrier, working, herding, foundation, non_sporting, sporting, misc)
        df['chosen'] = df['breed'].apply(lambda x: ifelse(x, dog_choice, "Yes", "No"))
        f=  (ggplot(dog_breed, aes('ltc'))
        +geom_density()
        +geom_vline(aes(xintercept= df['ltc'].iloc[0]),color='red', linetype='dashed')      
        +labs(x="Lifetime cost"))
        return f

    @output
    @render.table()
    @reactive.event(input.search2)
    async def group_description():
        dog_choice= input.breed()
        df= dog_breed.query('breed==@dog_choice')
        conn = psycopg2.connect(connection_info)
        cur = conn.cursor()
        group_description = pd.read_sql("select breed_group from dog_breed where breed=%s", conn, params=dog_choice)    
        lol= group.query(breed_group== group_description)

        cur.close()
        conn.close()
        return lol

    @output
    @render.text()
    @reactive.event(input.search2)
    async def breed_1():
        conn = psycopg2.connect(connection_info)
        cur = conn.cursor()
        breed_1 = pd.read_sql("select group_description from dog_group where breed_group =(select breed_group from dog_breed where breed=%s)", conn, params= input.breed())
        
        cur.close()
        conn.close()
        return breed_1

    @output
    @render.text()
    @reactive.event(input.search2)
    async def breed_2():
        dog_choice= input.breed()
        df= dog_breed.query('breed==@dog_choice')
        df= choose_group(df, hound, toy, terrier, working, herding, foundation, non_sporting, sporting, misc)
        conn = psycopg2.connect(connection_info)
        cur = conn.cursor()
        breed_2 = pd.read_sql("select group_description from dog_group where breed_group =(select breed_group from dog_breed where breed=%s)", conn, params= dog_choice)
        
        cur.close()
        conn.close()
        return breed_2

    @output
    @render.text()
    @reactive.event(input.search2)
    async def breed_3():
        dog_choice= input.breed()
        df= dog_breed.query('breed==@dog_choice')
        df= choose_group(df, hound, toy, terrier, working, herding, foundation, non_sporting, sporting, misc)
        conn = psycopg2.connect(connection_info)
        cur = conn.cursor()
        breed_3 = pd.read_sql("select group_description from dog_group where breed_group =(select breed_group from dog_breed where breed=%s)", conn, params= dog_choice)
        
        cur.close()
        conn.close()
        return breed_3
        
        


    @output
    @render.table()
    @reactive.event(input.search2)
    async def health():
        await asyncio.sleep(0.1)
        dog_choice= input.breed()
        return dog_breed.query('breed== @dog_choice')[['gen_number','gen_summary','congen','gen_paper']]

    @output
    @render.text()
    @reactive.event(input.search2)
    async def general_info_header():
        await asyncio.sleep(0.1)
        
        return f'General information about : {input.breed()}'

    
    
    @output
    @render.text()
    @reactive.event(input.search2)
    async def health_header():
        await asyncio.sleep(0.1)
        return f'Health information about : {input.breed()}'
    

    @output
    @render.table()
    @reactive.event(input.search2)
    async def info():
        await asyncio.sleep(0.1)
        dog_choice= input.breed()
        return dog_breed.query('breed== @dog_choice')[['breed', 'popularity', 'breed_group','size_cat', 'shedding_cat', 'int_cat', 'temperament1','temperament2', 'temperament3']]


    @output
    @render.text
    @reactive.event(input.signup)
    async def signup():
        #Additional mechanism for Searching
        with ui.Progress(min=1, max=15) as p:
            p.set(message="Creating Account", detail="This may take a while...")

            for i in range(1, 15):
                p.set(i, message="Creating Account")
                await asyncio.sleep(0.1)

        if input.user_breed()== "":
            user_own_breed= "None"
        else:
            user_own_breed= input.user_breed()

        conn = psycopg2.connect(connection_info)
        output_username= "Done Creating Account!"
        try:
        
            cursor = conn.cursor()
            
            # 값 변경 쿼리
            cursor.execute("INSERT INTO users values (%s,%s, %s)",(input.username(), input.password(), user_own_breed))
            
            # 트랜잭션 커밋 - 데이터베이스에 업데이트를 반영
            conn.commit()

            

        except psycopg2.Error as e:
            # 데이터베이스 에러 처리
            output_username= "DB error: There is already a user with this username!"
            # 롤백- 최근 커밋 이후의 transaction들을 모두 취소
            conn.rollback()
            
        finally:
            # 데이터베이스 연결 해제 필수!!
            conn.close()
        return output_username


    @output
    @render.text
    @reactive.event(input.hospitals)
    async def map():
        with ui.Progress(min=1, max=15) as p:
            p.set(message="Redirecting to nearest hospitals...")

            for i in range(1, 15):
                p.set(i, message="Redirecting")
                await asyncio.sleep(0.1)

        map = Map()
        map.showMap()

        return "Hospitals"


    
    @output
    @render.table()
    @reactive.event(input.signup)
    async def health_user():
        await asyncio.sleep(0.1)
        dog_choice= input.user_breed()
        return dog_breed.query('breed== @dog_choice')[['gen_number','gen_summary','congen','gen_paper']]

    @output
    @render.text()
    @reactive.event(input.signup)
    async def general_info_header_user():
        await asyncio.sleep(0.1)
        return f'General information about your dog : {input.user_breed()}'
    
    @output
    @render.text()
    @reactive.event(input.signup)
    async def health_header_user():
        await asyncio.sleep(0.1)
        return f'Health information about your dog : {input.user_breed()}'
    

    @output
    @render.table()
    @reactive.event(input.signup)
    async def info_user():
        await asyncio.sleep(0.1)
        dog_choice= input.user_breed()
        return dog_breed.query('breed== @dog_choice')[['breed', 'popularity', 'breed_group','size_cat', 'shedding_cat', 'int_cat', 'temperament1','temperament2', 'temperament3']]



    @output
    @render.plot()
    @reactive.event(input.signup)
    async def plot_user():
        await asyncio.sleep(0.1)
        dog_choice= input.user_breed()
        df= dog_breed.query('breed==@dog_choice')
        a=(ggplot(dog_breed)
        #groom value
        +geom_linerange(aes(ymin="0", ymax= "1", x=0.5),color="#3FCBAB",size=4)
        +geom_text(x= 0.5, y=-0.22, label="Grooming frequency",size= 9)
        +geom_text(x= 0.55, y=0.5, label=df['groom_cat'].iloc[0], size=9)
        +coord_flip()
        +geom_point(df, y= df['groom_value'].iloc[0], x=0.5, color='grey', size=3)
        #shedding value
        +geom_linerange(aes(ymin="0", ymax= "1", x=0.4),color="#3FCBAB",size=4)
        +geom_text(x= 0.4, y=-0.22, label="Shedding frequency",size= 9)
        +geom_text(x= 0.45, y=0.5, label=df['shedding_cat'].iloc[0], size=9)
        +coord_flip()
        +geom_point(df, y= df['shedding_value'].iloc[0], x=0.4, color='grey', size=3)
        #energy level value
        +geom_linerange(aes(ymin="0", ymax= "1", x=0.3),color="#3FCBAB",size=4)
        +geom_text(x= 0.3, y=-0.22, label="Energy Level",size= 9)
        +geom_text(x= 0.35, y=0.5, label=df['energy_level_cat'].iloc[0], size=9)
        +coord_flip()
        +geom_point(df, y= df['energy_level_value'].iloc[0], x=0.3, color='grey', size=3)
        #demeanor value
        +geom_linerange(aes(ymin="0", ymax= "1", x=0.2),color="#3FCBAB",size=4)
        +geom_text(x= 0.2, y=-0.22, label="Demeanor Value",size= 9)
        +geom_text(x= 0.25, y=0.5, label=df['demeanor_cat'].iloc[0], size=9)
        +coord_flip()
        +geom_point(df, y= df['demeanor_value'].iloc[0], x=0.2, color='grey', size=3)
        #trainability value
        +geom_linerange(aes(ymin="0", ymax= "1", x=0.1),color="#3FCBAB",size=4)
        +geom_text(x= 0.1, y=-0.22, label="Trainability",size= 9)
        +geom_text(x= 0.15, y=0.5, label=df['trainability_cat'].iloc[0], size=9)
        +coord_flip()
        +geom_point(df, y= df['trainability_value'].iloc[0], x=0.1, color='grey', size=3)
        #axis
        +ylim(-0.4,1)
        +xlim(0.08,0.55)
        +labs(x=("Traits of "+ df['breed'].iloc[0])))        
        return a

    @output
    @render.plot()
    @reactive.event(input.signup)
    async def life_expect_plot_user():
        dog_choice= input.user_breed()
        df= dog_breed.query('breed==@dog_choice')
        df= choose_group(df, hound, toy, terrier, working, herding, foundation, non_sporting, sporting, misc)
        df['chosen'] = df['breed'].apply(lambda x: ifelse(x, dog_choice, "Yes", "No"))
        b=(ggplot(df, aes(x="reorder(breed, (min_expectancy+max_expectancy)/2)", y= "(min_expectancy+max_expectancy)/2"))
        + geom_linerange(aes(ymin='min_expectancy', ymax= "max_expectancy", color="chosen"),size=2)
        + geom_point(color = "black", size= 0.5, alpha= 0.3)
        + coord_flip()
        + scale_colour_manual(values = ("#D8D0CF", "#3FCBAB"))
        + theme(legend_position='none')
        + labs(x="Breed", y="Life Expectancy Range(years)"))
        return b


    @output
    @render.plot()
    @reactive.event(input.signup)
    async def weight_plot_user():
        dog_choice= input.user_breed()
        df= dog_breed.query('breed==@dog_choice')
        df= choose_group(df, hound, toy, terrier, working, herding, foundation, non_sporting, sporting, misc)
        df['chosen'] = df['breed'].apply(lambda x: ifelse(x, dog_choice, "Yes", "No"))
        c=(ggplot(df, aes(x="reorder(breed, (min_weight+max_weight)/2)", y= "(min_weight+max_weight)/2"))
        + geom_linerange(aes(ymin="min_weight", ymax= "max_weight", color="chosen"),size=2)
        + geom_point(color="black", size= 0.5,alpha=0.3)
        + coord_flip()
        + scale_colour_manual(values = ("#D8D0CF", "#3FCBAB"))
        + theme(legend_position='none')
        + labs(x="Breed", y="Weight Range(kg)"))
        return c

    @output
    @render.plot()
    @reactive.event(input.signup)
    async def height_plot_user():
        dog_choice= input.user_breed()
        df= dog_breed.query('breed==@dog_choice')
        df= choose_group(df, hound, toy, terrier, working, herding, foundation, non_sporting, sporting, misc)
        df['chosen'] = df['breed'].apply(lambda x: ifelse(x, dog_choice, "Yes", "No"))
        d=(ggplot(df, aes(x="reorder(breed, (min_height+max_height)/2)", y= "(min_height+max_height)/2"))
        + geom_linerange(aes(ymin="min_height", ymax= "max_height", color="chosen"),size=2)
        + geom_point(color="black", size= 0.5,alpha =0.3)
        + coord_flip()
        + scale_colour_manual(values = ("#D8D0CF", "#3FCBAB"))
        + theme(legend_position='none')
        + labs(x="Breed", y="Height Range(cm)"))
        return d

    @output
    @render.plot()
    @reactive.event(input.signup)
    async def cmd_plot_user():
        dog_choice= input.user_breed()
        df= dog_breed.query('breed==@dog_choice')
        df= choose_group(df, hound, toy, terrier, working, herding, foundation, non_sporting, sporting, misc)
        df['chosen'] = df['breed'].apply(lambda x: ifelse(x, dog_choice, "Yes", "No"))
        e=(ggplot(choose_group(df, hound, toy, terrier,working, herding, foundation, non_sporting, sporting, misc), aes(x="reorder(breed, (comm_min+comm_max)/2)", y= "(comm_min+comm_max)/2"))
        + geom_linerange(aes(ymin="comm_min", ymax= "comm_max", color="chosen"),size=2)
        + geom_point(color="black", size= 0.5,alpha=0.3)
        + coord_flip()
        + scale_colour_manual(values = ("#D8D0CF", "#3FCBAB"))
        + theme(legend_position='none')
        + labs(x="Breed", y="Repetitions to understand new command"))
        return e


    @output
    @render.plot()
    @reactive.event(input.signup)
    async def ltc_plot_user():
        dog_choice= input.user_breed()
        df= dog_breed.query('breed==@dog_choice')
        df= choose_group(df, hound, toy, terrier, working, herding, foundation, non_sporting, sporting, misc)
        df['chosen'] = df['breed'].apply(lambda x: ifelse(x, dog_choice, "Yes", "No"))
        f=  (ggplot(dog_breed, aes('ltc'))
        +geom_density()
        +geom_vline(aes(xintercept= df['ltc'].iloc[0]),color='red', linetype='dashed')
        +geom_text(x=20000, y= 0.00013, label=("Lifetime cost of "+ df['breed'].iloc[0]+ " is: "+ str(df['ltc'].iloc[0])),size= 9)          
        +labs(x="Lifetime cost"))
        return f

    



app = App(app_ui, server)

