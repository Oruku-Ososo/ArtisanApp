#!/usr/bin/env python3

chapters = [
    ("Genesis Chapter 1", "The Creation", "genesis_01.html", 
     "The creation of heaven and earth in six days, with God resting on the seventh.",
     "God creates light, sky, land, vegetation, celestial bodies, sea creatures, birds, land animals, and finally humanity in His image."),
    
    ("Genesis Chapter 2", "Eden and the First Humans", "genesis_02.html",
     "A more detailed account of man's creation and the Garden of Eden.",
     "God forms Adam from dust, places him in Eden, creates Eve from Adam's rib, and establishes marriage."),
    
    ("Genesis Chapter 3", "The Fall of Man", "genesis_03.html",
     "The temptation, fall, and expulsion from Eden.",
     "The serpent tempts Eve, both eat the forbidden fruit, God pronounces judgment, and they are expelled from the Garden."),
    
    ("Genesis Chapter 4", "Cain and Abel", "genesis_04.html",
     "The first murder and its consequences.",
     "Cain kills his brother Abel out of jealousy, is marked by God, and becomes a wanderer. The lineage of Cain is recorded."),
    
    ("Genesis Chapter 5", "The Genealogy from Adam to Noah", "genesis_05.html",
     "The descendants of Adam through Seth.",
     "Records the genealogy from Adam to Noah, noting the ages and deaths of the patriarchs, with Enoch walking with God."),
    
    ("Genesis Chapter 6", "The Wickedness of Humanity", "genesis_06.html",
     "God's decision to send the flood.",
     "Humanity's wickedness grieves God. Noah finds favor. Instructions for building the ark are given."),
    
    ("Genesis Chapter 7", "The Flood Begins", "genesis_07.html",
     "Noah enters the ark and the flood waters come.",
     "Noah, his family, and the animals enter the ark. Rain falls for 40 days and nights, covering the earth."),
    
    ("Genesis Chapter 8", "The Waters Recede", "genesis_08.html",
     "The flood ends and the earth dries.",
     "God remembers Noah, the waters recede, birds are sent to test dry land, and they exit the ark."),
    
    ("Genesis Chapter 9", "God's Covenant with Noah", "genesis_09.html",
     "The rainbow covenant and new beginning.",
     "God establishes covenant with rainbow as sign, gives new dietary laws, and Noah's family repopulates the earth."),
    
    ("Genesis Chapter 10", "The Table of Nations", "genesis_10.html",
     "Descendants of Noah's three sons.",
     "Genealogies of Japheth, Ham, and Shem, showing how nations spread across the earth after the flood."),
    
    ("Genesis Chapter 11", "The Tower of Babel", "genesis_11.html",
     "Human pride and the confusion of languages.",
     "Humanity builds a tower to reach heaven. God confuses their languages and scatters them. Genealogy from Shem to Abram."),
    
    ("Genesis Chapter 12", "The Call of Abram", "genesis_12.html",
     "God's promise to Abram.",
     "God calls Abram to leave his country, promises to make him a great nation. Abram goes to Canaan and Egypt."),
    
    ("Genesis Chapter 13", "Abram and Lot Separate", "genesis_13.html",
     "Division between Abram and Lot.",
     "Conflict between herdsmen leads to separation. Lot chooses Sodom. God renews promises to Abram."),
    
    ("Genesis Chapter 14", "Abram Rescues Lot", "genesis_14.html",
     "War of the kings and Melchizedek.",
     "Lot is captured in war. Abram rescues him. Melchizedek blesses Abram, who gives him a tenth."),
    
    ("Genesis Chapter 15", "God's Covenant with Abram", "genesis_15.html",
     "The covenant ceremony.",
     "God promises Abram an heir and countless descendants. Covenant is ratified through sacrifice."),
    
    ("Genesis Chapter 16", "Hagar and Ishmael", "genesis_16.html",
     "Sarai's plan and its consequences.",
     "Sarai gives Hagar to Abram. Hagar conceives, flees, but returns after angel's visit. Ishmael is born."),
    
    ("Genesis Chapter 17", "The Covenant of Circumcision", "genesis_17.html",
     "Name changes and the sign of covenant.",
     "Abram becomes Abraham, Sarai becomes Sarah. Circumcision instituted. Promise of Isaac reaffirmed."),
    
    ("Genesis Chapter 18", "Visitors at Mamre", "genesis_18.html",
     "Three visitors and the promise of Isaac.",
     "Three men visit Abraham. Sarah laughs at promise of son. Abraham intercedes for Sodom."),
    
    ("Genesis Chapter 19", "Sodom and Gomorrah Destroyed", "genesis_19.html",
     "Judgment on the cities of the plain.",
     "Angels rescue Lot. Cities are destroyed. Lot's wife looks back. Lot's daughters bear Moab and Ammon."),
    
    ("Genesis Chapter 20", "Abraham and Abimelech", "genesis_20.html",
     "Abraham's deception in Gerar.",
     "Abraham claims Sarah is his sister. Abimelech takes her but returns her after God's warning."),
    
    ("Genesis Chapter 21", "Birth of Isaac", "genesis_21.html",
     "Isaac is born; Hagar and Ishmael sent away.",
     "Isaac is born to Sarah. Hagar and Ishmael are sent away but God provides. Treaty with Abimelech."),
    
    ("Genesis Chapter 22", "The Testing of Abraham", "genesis_22.html",
     "Abraham's willingness to sacrifice Isaac.",
     "God tests Abraham by commanding sacrifice of Isaac. Angel stops him. Ram provided. Blessings renewed."),
    
    ("Genesis Chapter 23", "Death of Sarah", "genesis_23.html",
     "Sarah dies and is buried.",
     "Sarah dies at 127. Abraham buys cave of Machpelah from Ephron as burial place."),
    
    ("Genesis Chapter 24", "A Wife for Isaac", "genesis_24.html",
     "Finding Rebekah.",
     "Abraham's servant prays for guidance, meets Rebekah at well, she agrees to marry Isaac."),
    
    ("Genesis Chapter 25", "Death of Abraham", "genesis_25.html",
     "Abraham's later years and death.",
     "Abraham marries Keturah, has more children. Dies at 175. Esau and Jacob born to Isaac."),
    
    ("Genesis Chapter 26", "Isaac and Abimelech", "genesis_26.html",
     "Isaac in Gerar.",
     "Isaac repeats Abraham's deception. God renews covenant. Disputes over wells resolved."),
    
    ("Genesis Chapter 27", "Jacob Gets Isaac's Blessing", "genesis_27.html",
     "Deception and stolen blessing.",
     "Rebekah helps Jacob deceive Isaac and receive blessing meant for Esau. Esau vows revenge."),
    
    ("Genesis Chapter 28", "Jacob's Dream at Bethel", "genesis_28.html",
     "Jacob flees and dreams of ladder.",
     "Jacob flees to Haran. Dreams of ladder to heaven. God renews covenant. Jacob vows to serve God."),
    
    ("Genesis Chapter 29", "Jacob Marries Leah and Rachel", "genesis_29.html",
     "Seven years for Rachel, deceived into marrying Leah.",
     "Jacob meets Rachel, works seven years, is tricked into marrying Leah first, then Rachel."),
    
    ("Genesis Chapter 30", "Jacob's Children Born", "genesis_30.html",
     "Birth of Jacob's twelve sons.",
     "Rachel and Leah compete through maidservants. Eleven sons and one daughter born to Jacob."),
    
    ("Genesis Chapter 31", "Jacob Flees from Laban", "genesis_31.html",
     "Departure from Haran.",
     "Jacob leaves secretly. Laban pursues. Covenant made at Mizpah. They part in peace."),
    
    ("Genesis Chapter 32", "Jacob Wrestles with God", "genesis_32.html",
     "Preparation to meet Esau.",
     "Jacob sends gifts ahead. Wrestles with man/God at Peniel. Name changed to Israel. Meets Esau."),
    
    ("Genesis Chapter 33", "Jacob and Esau Reconcile", "genesis_33.html",
     "Brothers reunite.",
     "Esau welcomes Jacob warmly. They part ways. Jacob settles near Shechem."),
    
    ("Genesis Chapter 34", "Dinah and the Shechemites", "genesis_34.html",
     "Tragedy at Shechem.",
     "Dinah is violated by Shechem. Brothers deceive and kill the men. Jacob rebukes them."),
    
    ("Genesis Chapter 35", "Return to Bethel", "genesis_35.html",
     "Jacob returns to promised land.",
     "God tells Jacob to return to Bethel. Rachel dies birthing Benjamin. Isaac dies."),
    
    ("Genesis Chapter 36", "Esau's Descendants", "genesis_36.html",
     "Genealogy of Edom.",
     "Records Esau's descendants and the chiefs of Edom before Israel had kings."),
    
    ("Genesis Chapter 37", "Joseph's Dreams", "genesis_37.html",
     "Joseph sold into slavery.",
     "Joseph's dreams anger brothers. They sell him to Ishmaelites. He goes to Egypt."),
    
    ("Genesis Chapter 38", "Judah and Tamar", "genesis_38.html",
     "Judah's family line.",
     "Judah's sons die. Tamar tricks Judah. Twins Perez and Zerah born."),
    
    ("Genesis Chapter 39", "Joseph in Potiphar's House", "genesis_39.html",
     "Joseph's rise and fall in Egypt.",
     "Joseph prospers in Potiphar's house. Resists Potiphar's wife. Falsely accused and imprisoned."),
    
    ("Genesis Chapter 40", "Joseph Interprets Dreams", "genesis_40.html",
     "Cupbearer and baker's dreams.",
     "In prison, Joseph interprets dreams for Pharaoh's officials. Cupbearer restored, baker executed."),
    
    ("Genesis Chapter 41", "Pharaoh's Dreams", "genesis_41.html",
     "Joseph interprets for Pharaoh.",
     "Pharaoh dreams of cows and grain. Joseph interprets: seven years plenty, seven famine. Made ruler of Egypt."),
    
    ("Genesis Chapter 42", "First Journey to Egypt", "genesis_42.html",
     "Brothers seek grain.",
     "Famine drives brothers to Egypt. Joseph recognizes them. Tests them. Simeon held hostage."),
    
    ("Genesis Chapter 43", "Second Journey to Egypt", "genesis_43.html",
     "Benjamin brought to Egypt.",
     "Famine continues. Brothers return with Benjamin. Joseph tests further. Feast together."),
    
    ("Genesis Chapter 44", "The Silver Cup", "genesis_44.html",
     "Benjamin accused of theft.",
     "Joseph's cup placed in Benjamin's sack. Brothers return. Judah offers himself for Benjamin."),
    
    ("Genesis Chapter 45", "Joseph Reveals Himself", "genesis_45.html",
     "Identity revealed; family reunion planned.",
     "Joseph reveals identity. Forgives brothers. Plans for family to move to Goshen."),
    
    ("Genesis Chapter 46", "Jacob Goes to Egypt", "genesis_46.html",
     "Israel migrates to Egypt.",
     "God assures Jacob. Family list given. Jacob and Joseph reunited. Settled in Goshen."),
    
    ("Genesis Chapter 47", "Settling in Goshen", "genesis_47.html",
     "Life during famine.",
     "Family presented to Pharaoh. Joseph manages famine. People sell land for food."),
    
    ("Genesis Chapter 48", "Manasseh and Ephraim", "genesis_48.html",
     "Jacob blesses Joseph's sons.",
     "Jacob adopts Joseph's sons. Crosses hands to bless younger over older. Prophecies given."),
    
    ("Genesis Chapter 49", "Jacob's Final Blessings", "genesis_49.html",
     "Prophecies over twelve sons.",
     "Jacob gathers sons, prophesies over each. Predicts Messiah from Judah. Dies at 147."),
    
    ("Genesis Chapter 50", "Death of Jacob and Joseph", "genesis_50.html",
     "Burial of Jacob; end of Genesis.",
     "Jacob embalmed and buried in Canaan. Joseph reassures brothers. Joseph dies at 110."),
]

html_template = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@400;700&family=IM+Fell+English:ital@0;1&display=swap');
        
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        
        body {{
            font-family: 'IM Fell English', serif;
            background: linear-gradient(135deg, #f5e6d3 0%, #e8d5b5 50%, #d4c4a8 100%);
            min-height: 100vh;
            padding: 40px 20px;
            line-height: 1.8;
            color: #3d2817;
        }}
        
        .container {{
            max-width: 900px;
            margin: 0 auto;
            background: rgba(255, 253, 240, 0.9);
            border: 3px solid #8b6f47;
            border-radius: 8px;
            box-shadow: 0 10px 40px rgba(61, 40, 23, 0.3);
            padding: 50px;
            position: relative;
        }}
        
        .container::before {{
            content: '';
            position: absolute;
            top: 10px; left: 10px; right: 10px; bottom: 10px;
            border: 2px solid #c9a961;
            border-radius: 4px;
            pointer-events: none;
        }}
        
        h1 {{
            font-family: 'Cinzel', serif;
            font-size: 2.8em;
            text-align: center;
            color: #5c4033;
            margin-bottom: 30px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
            border-bottom: 3px double #8b6f47;
            padding-bottom: 20px;
        }}
        
        h2 {{
            font-family: 'Cinzel', serif;
            font-size: 1.8em;
            color: #6b4423;
            margin: 30px 0 15px 0;
            border-left: 4px solid #8b6f47;
            padding-left: 15px;
        }}
        
        p {{
            font-size: 1.2em;
            text-align: justify;
            margin-bottom: 20px;
            text-indent: 40px;
        }}
        
        .verse {{
            background: rgba(212, 196, 168, 0.3);
            padding: 20px;
            border-left: 4px solid #6b4423;
            margin: 25px 0;
            font-style: italic;
            border-radius: 0 8px 8px 0;
        }}
        
        .image-placeholder {{
            width: 100%;
            height: 400px;
            background: linear-gradient(45deg, #2c1810 0%, #4a3423 50%, #2c1810 100%);
            border: 4px solid #8b6f47;
            border-radius: 8px;
            margin: 30px 0;
            display: flex;
            align-items: center;
            justify-content: center;
            color: #f5e6d3;
            font-family: 'Cinzel', serif;
            font-size: 1.3em;
            text-align: center;
            padding: 30px;
            position: relative;
            overflow: hidden;
        }}
        
        .image-placeholder::after {{
            content: '📜';
            font-size: 4em;
            opacity: 0.3;
            position: absolute;
        }}
        
        .chapter-nav {{
            display: flex;
            justify-content: space-between;
            margin-top: 40px;
            padding-top: 30px;
            border-top: 2px solid #8b6f47;
        }}
        
        .chapter-nav a {{
            font-family: 'Cinzel', serif;
            color: #5c4033;
            text-decoration: none;
            padding: 10px 25px;
            border: 2px solid #8b6f47;
            border-radius: 4px;
            transition: all 0.3s ease;
        }}
        
        .chapter-nav a:hover {{
            background: #8b6f47;
            color: #f5e6d3;
        }}
        
        .ornament {{
            text-align: center;
            font-size: 2em;
            color: #8b6f47;
            margin: 30px 0;
        }}
        
        ul {{ margin-left: 40px; margin-bottom: 20px; }}
        li {{ margin-bottom: 10px; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>{title}<br><small style="font-size: 0.5em; font-style: italic;">{subtitle}</small></h1>
        
        <div class="image-placeholder">
            [SOTA Graphics: {scene_description}]
        </div>
        
        <h2>Overview</h2>
        <p>{overview}</p>
        
        <h2>Detailed Account</h2>
        <p>{detailed_account}</p>
        
        <h2>Key Themes and Lessons</h2>
        <p>This chapter reveals important truths about God's character, human nature, and the unfolding of divine providence. The narrative demonstrates God's faithfulness to His promises despite human failings, His justice in dealing with sin, and His mercy in providing redemption.</p>
        
        <h2>Historical and Cultural Context</h2>
        <p>Understanding the ancient Near Eastern context enriches our reading of this text. The practices, customs, and worldview reflected here provide insight into the lives of the patriarchs and God's interaction with them within their historical setting.</p>
        
        <div class="ornament">❖ ❖ ❖</div>
        
        <p>The story continues to resonate through millennia, offering wisdom, comfort, and challenge to readers today. Each generation discovers new depths in these ancient words, finding relevance for contemporary life while connecting with the timeless truths they convey.</p>
        
        <div class="image-placeholder">
            [SOTA Graphics: Artistic interpretation of {artistic_scene}]
        </div>
        
        <div class="chapter-nav">
            {prev_link}
            {next_link}
        </div>
    </div>
</body>
</html>'''

for i, (title, subtitle, filename, overview, detailed) in enumerate(chapters):
    chapter_num = i + 1
    
    if chapter_num == 1:
        prev_link = "<span></span>"
    else:
        prev_num = str(chapter_num - 1).zfill(2)
        prev_link = f'<a href="genesis_{prev_num}.html">← Previous: Chapter {chapter_num - 1}</a>'
    
    if chapter_num == 50:
        next_link = "<span></span>"
    else:
        next_num = str(chapter_num + 1).zfill(2)
        next_link = f'<a href="genesis_{next_num}.html">Next: Chapter {chapter_num + 1} →</a>'
    
    scene_desc = f"Ancient biblical scene depicting {subtitle.lower()}, with dramatic lighting and period-authentic details"
    artistic_scene = f"{subtitle.lower()} in classical artistic style"
    
    content = html_template.format(
        title=title,
        subtitle=subtitle,
        scene_description=scene_desc,
        overview=overview,
        detailed_account=detailed,
        artistic_scene=artistic_scene,
        prev_link=prev_link,
        next_link=next_link
    )
    
    filepath = f"/workspace/Bibliteka/Genesis_Chapters/{filename}"
    with open(filepath, 'w') as f:
        f.write(content)
    print(f"Created {filename}")

print("\nAll 50 chapters generated successfully!")
