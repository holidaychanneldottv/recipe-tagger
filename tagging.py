import os
import socket
from dotenv import load_dotenv
from sqlalchemy import create_engine, text, event
from sqlalchemy.pool import NullPool
from collections import defaultdict

orig_getaddrinfo = socket.getaddrinfo
def getaddrinfo_ipv4_only(*args, **kwargs):
    return [info for info in orig_getaddrinfo(*args, **kwargs) if info[0] == socket.AF_INET]
socket.getaddrinfo = getaddrinfo_ipv4_only

load_dotenv()

DATABASE_URL = os.getenv("POSTGRES_URL") 
print("Database URL:", DATABASE_URL)
DB_NAME = os.getenv("DB_NAME")
engine = create_engine(DATABASE_URL, poolclass=NullPool)


# Tag - tag key words mapping

holiday_keywords = {
    "Thanksgiving": ['turkey', 'roast turkey', 'smoked turkey', 'fried turkey', 'turkey breast', 'turkey legs', 'turkey gravy', 'gravy', 'ham', 'glazed ham', 'roast beef', 'prime rib', 'mashed potatoes', 'roasted potatoes', 'sweet potatoes', 'sweet potato casserole', 'candied yams', 'scalloped potatoes', 'au gratin potatoes', 'stuffing', 'dressing', 'cornbread dressing', 'sausage stuffing', 'herb stuffing', 'bread stuffing', 'green bean casserole', 'green beans', 'brussels sprouts', 'roasted vegetables', 'glazed carrots', 'corn', 'creamed corn', 'corn pudding', 'squash', 'butternut squash', 'acorn squash', 'roasted squash', 'collard greens', 'turnip greens', 'cranberry sauce', 'cranberry relish', 'macaroni and cheese', 'mac & cheese', 'dinner rolls', 'biscuits', 'cornbread', 'pumpkin pie', 'apple pie', 'pecan pie', 'sweet potato pie', 'apple cobbler', 'pumpkin cheesecake', 'pecan tassies', 'cranberry tart', 'sage', 'rosemary', 'thyme', 'poultry seasoning', 'cinnamon', 'nutmeg', 'ginger', 'cloves', 'allspice', 'cranberries', 'apples', 'pecans', 'walnuts', 'chestnuts', 'butter', 'cream', 'brown sugar', 'maple syrup', 'marshmallows', 'thanksgiving', 'turkey day', 'holiday', 'feast', 'harvest', 'family dinner', 'leftovers', 'friendsgiving', 'autumn', 'fall'],
    "Independence Day": ['4th of july', 'independence day', 'barbecue', 'bbq', 'grill', 'grilling', 'cookout', 'picnic', 'summer', 'patriotic', 'red white and blue', 'hamburger', 'burger', 'cheeseburger', 'hot dog', 'frankfurter', 'sausage', 'bratwurst', 'ribs', 'baby back ribs', 'pork ribs', 'bbq chicken', 'grilled chicken', 'pulled pork', 'pulled chicken', 'steak', 'kabobs', 'kebabs', 'shish kebab', 'corn on the cob', 'grilled corn', 'potato salad', 'coleslaw', 'slaw', 'macaroni salad', 'pasta salad', 'baked beans', 'three-bean salad', 'cornbread', 'deviled eggs', 'watermelon', 'fruit salad', 'berry salad', 'strawberry', 'blueberry', 'raspberry', 'flag cake', 'trifle', 'berry trifle', 'pie', 'apple pie', 'cherry pie', 'blueberry pie', 'peach cobbler', 'cobbler', 'shortcake', 'strawberry shortcake', 'ice cream', 'ice cream cake', 'popsicles', 'lemonade', 'iced tea', 'sweet tea', 's\'mores', 'fireworks', 'stars and stripes'],
    "Memorial Day": ['memorial day', 'memorial day weekend', 'barbecue', 'bbq', 'grill', 'grilling', 'cookout', 'picnic', 'summer', 'hamburger', 'burger', 'hot dog', 'ribs', 'grilled chicken', 'kabobs', 'potato salad', 'coleslaw', 'pasta salad', 'baked beans', 'corn on the cob', 'deviled eggs', 'watermelon', 'fruit salad', 'strawberry', 'blueberry', 'lemonade', 'iced tea', 's\'mores', 'patriotic', 'red white and blue'],
    "Labor Day": ['labor day', 'labor day weekend', 'end of summer', 'barbecue', 'bbq', 'grill', 'grilling', 'cookout', 'picnic', 'hamburger', 'burger', 'hot dog', 'ribs', 'pulled pork', 'grilled chicken', 'corn on the cob', 'potato salad', 'coleslaw', 'pasta salad', 'baked beans', 'watermelon', 'lemonade', 'iced tea'],
    "Veterans Day": ['veterans day', 'veteran', 'comfort food', 'american', 'hearty', 'diner food', 'pancakes', 'free meal', 'apple pie', 'roast chicken', 'pot roast', 'casserole', 'stew', 'chili', 'soup'],
    "New Year’s Day": ['new year’s', 'new years eve', 'new years day', 'appetizer', 'finger food', 'cocktail', 'champagne', 'prosecco', 'sparkling wine', 'canapes', 'dips', 'shrimp cocktail', 'wings', 'meatballs', 'fondue', 'black-eyed peas', 'collard greens', 'pork', 'sauerkraut', 'lentils', 'grapes', 'cornbread', 'good luck', 'brunch', 'casserole'],
    "Presidents’ Day": ['presidents’ day', 'presidents day', 'cherry', 'cherry pie', 'cherry dessert', 'american', 'colonial', 'heritage recipes', 'hoecakes', 'pancakes', 'pot pie', 'braised cabbage', 'stew', 'apple pie'],
    "Martin Luther King Jr. Day": ['martin luther king jr. day', 'mlk day', 'soul food', 'southern food', 'comfort food', 'fried chicken', 'collard greens', 'mac and cheese', 'cornbread', 'sweet potato pie', 'pound cake', 'banana pudding', 'peach cobbler'],
    "Juneteenth": ['juneteenth', 'freedom day', 'emancipation day', 'red drink', 'hibiscus tea', 'strawberry soda', 'red soda', 'barbecue', 'bbq', 'collard greens', 'black-eyed peas', 'sweet potatoes', 'cornbread', 'red velvet cake', 'strawberry pie', 'watermelon', 'southern food', 'soul food', 'fish fry'],
    "Columbus Day": ['columbus day', 'italian-american', 'italian', 'pasta', 'lasagna', 'baked ziti', 'spaghetti', 'meatballs', 'sausage and peppers', 'antipasto', 'cannoli', 'pesto', 'marinara', 'chicken parmigiana', 'gnocchi'],
    "Halloween": ['halloween', 'spooky', 'creepy', 'haunted', 'monster', 'ghost', 'witch', 'spider', 'eyeball', 'pumpkin', 'pumpkin spice', 'pumpkin seeds', 'candy', 'caramel apple', 'candy apple', 'popcorn balls', 'apple cider', 'chili', 'fall', 'autumn', 'treats', 'cupcakes', 'cookies', 'brownies', 'stew', 'soup'],
    "Earth Day": ['earth day', 'sustainable', 'eco-friendly', 'plant-based', 'vegan', 'vegetarian', 'local', 'seasonal', 'organic', 'farm-to-table', 'farmers market', 'salad', 'smoothie', 'veggie burger', 'herb', 'edible flowers', 'whole grain', 'granola', 'zerowaste', 'compost', 'gardening'], 
    "Mother's Day": ['mother\'s day', 'brunch', 'breakfast in bed', 'mimosa', 'bellini', 'quiche', 'frittata', 'crepes', 'scones', 'croissant', 'eggs benedict', 'strata', 'cake', 'cupcakes', 'macarons', 'tea party', 'finger sandwiches', 'salad', 'pasta salad', 'seafood', 'salmon', 'shrimp', 'lemon', 'asparagus', 'berries', 'strawberry', 'raspberry', 'edible flowers', 'prosecco', 'rosé'],
    "Father's Day": ['father\'s day', 'barbecue', 'bbq', 'grill', 'grilling', 'steak', 'ribs', 'burgers', 'cheeseburger', 'brisket', 'pulled pork', 'wings', 'chicken wings', 'beer', 'whiskey', 'bacon', 'potatoes', 'potato skins', 'onion rings', 'nachos', 'chili', 'surf and turf', 'lobster', 'brownies', 'chocolate cake'],
    "Christmas": ['christmas', 'xmas', 'holiday', 'roast turkey', 'roast beef', 'prime rib', 'glazed ham', 'goose', 'stuffing', 'dressing', 'gravy', 'mashed potatoes', 'roasted vegetables', 'brussels sprouts', 'cranberry sauce', 'yule log', 'buche de noel', 'christmas cookies', 'sugar cookies', 'gingerbread', 'fruitcake', 'panettone', 'stollen', 'peppermint', 'eggnog', 'mulled wine', 'hot chocolate', 'candy cane'],
    "Easter": ['easter', 'roast lamb', 'glazed ham', 'deviled eggs', 'scalloped potatoes', 'au gratin potatoes', 'asparagus', 'carrots', 'spring peas', 'hot cross buns', 'easter bread', 'kulich', 'tsoureki', 'babka', 'carrot cake', 'coconut cake', 'lemon tart', 'cadbury eggs', 'chocolate eggs', 'jelly beans', 'easter brunch', 'quiche'],
    "Hanukkah": ['hanukkah', 'chanukah', 'latkes', 'potato pancakes', 'sufganiyot', 'jelly donuts', 'brisket', 'kugel', 'noodle kugel', 'challah', 'gelt', 'chocolate coins', 'applesauce', 'sour cream', 'fried food'],
    "Passover": ['passover', 'pesach', 'seder', 'matzo', 'matzah', 'matzo ball soup', 'gefilte fish', 'charoset', 'maror', 'horseradish', 'brisket', 'roast chicken', 'tzimmes', 'kugel', 'potato kugel', 'macaroons', 'unleavened', 'chametz-free', 'kitniyot'],
    "Ramadan": ['ramadan', 'iftar', 'suhoor', 'fasting', 'dates', 'lentil soup', 'shorba', 'harira', 'samosa', 'sambousek', 'stuffed vegetables', 'maqluba', 'biryani', 'kebab', 'stew', 'tagine', 'fattoush', 'hummus', 'kunafa', 'qatayef', 'fruit juice', 'vimto'],
    "Eid al-Fitr": ['eid al-fitr', 'eid', 'maamoul', 'kahk', 'eid cookies', 'samosa', 'biryani', 'korma', 'seviyan', 'sheer khurma', 'baklava', 'kunafa', 'basbousa', 'halwa', 'sweets', 'feast', 'celebration'],
    "Eid al-Adha": ['eid al-adha', 'eid', 'lamb', 'mutton', 'goat', 'beef', 'kebab', 'biryani', 'korma', 'haleem', 'tagine', 'roast leg of lamb', 'grilled meat', 'barbecue', 'sacrifice', 'feast'],
    "Diwali": ['diwali', 'deepavali', 'mithai', 'ladoo', 'laddu', 'barfi', 'jalebi', 'gulab jamun', 'kaju katli', 'halwa', 'samosa', 'pakora', 'kachori', 'chivda', 'namkeen', 'mathri', 'chakli', 'feast', 'sweets'],
    "Holi": ['holi', 'thandai', 'bhang', 'gujiya', 'malpua', 'dahi vada', 'kanji', 'puran poli', 'samosa', 'pakora', 'kachori', 'mathri', 'lassi', 'sweets', 'snacks'],
    "Rosh Hashanah": ['rosh hashanah', 'apples and honey', 'honey cake', 'round challah', 'pomegranate', 'lekach', 'honey', 'brisket', 'roast chicken', 'gefilte fish', 'tzimmes', 'kugel', 'sweet new year', 'shana tova'],
    "Yom Kippur": ['yom kippur', 'break the fast', 'pre-fast meal', 'bagels', 'lox', 'cream cheese', 'kugel', 'noodle kugel', 'blintzes', 'deli platter', 'whitefish salad', 'egg salad', 'challah', 'honey cake', 'tea', 'coffee', 'fasting'],
    "Orthodox Easter": ['orthodox easter', 'pascha', 'tsoureki', 'magiritsa', 'lamb', 'roast lamb', 'kokoretsi', 'red eggs', 'paska', 'kulich', 'easter bread', 'cheese pie', 'tiropita'],
    "Orthodox Christmas": ['orthodox christmas', 'holy supper', 'kutia', 'kutya', 'borscht', 'sauerkraut', 'cabbage rolls', 'holubtsi', 'varenyky', 'pierogi', 'fish', 'herring', 'mushrooms', 'pampushky', 'uzvar', 'kompot'],
    "Kwanzaa": ['kwanzaa', 'karamu', 'soul food', 'african cuisine', 'caribbean food', 'jollof rice', 'collard greens', 'black-eyed peas', 'fried chicken', 'catfish', 'jerk chicken', 'gumbo', 'peanut stew', 'sweet potato pie', 'cornbread', 'benne wafers', 'mazao'],
    "Chinese New Year": ['chinese new year', 'lunar new year', 'spring festival', 'dumplings', 'jiaozi', 'potstickers', 'fish', 'spring rolls', 'egg rolls', 'niangao', 'rice cake', 'tangyuan', 'longevity noodles', 'good luck', 'prosperity', 'reunion dinner'],
    "Navratri": ['navratri', 'fasting', 'vrat', 'sabudana', 'kuttu', 'singhara', 'rajgira', 'samak rice', 'paneer', 'potatoes', 'sweet potato', 'fruit', 'makhana', 'peanuts', 'sendha namak', 'vegetarian', 'satvik'],
    "Game Day / Super Bowl": ['super bowl', 'game day', 'party', 'appetizer', 'finger food', 'wings', 'chicken wings', 'buffalo wings', 'nachos', 'chili', 'sliders', 'pulled pork', 'pizza', 'dip', 'guacamole', 'salsa', 'queso', 'seven-layer dip', 'spinach artichoke dip', 'potato skins', 'mozzarella sticks', 'jalapeno poppers', 'pigs in a blanket', 'beer', 'soda'],
    "Valentine’s Day": ['valentine\'s day', 'romantic dinner', 'chocolate', 'dark chocolate', 'chocolate lava cake', 'chocolate covered strawberries', 'truffles', 'fondue', 'strawberries', 'raspberries', 'champagne', 'sparkling wine', 'prosecco', 'steak', 'scallops', 'lobster', 'oysters', 'pasta', 'red wine', 'heart-shaped', 'dessert for two', 'romantic', 'aphrodisiac'],
    "St. Patrick’s Day": ['st. patrick\'s day', 'paddy\'s day', 'irish', 'corned beef', 'cabbage', 'corned beef and cabbage', 'soda bread', 'colcannon', 'shepherd\'s pie', 'irish stew', 'guinness', 'stout', 'irish coffee', 'potatoes', 'green beer', 'shamrock', 'mint', 'baileys', 'irish cream', 'reuben', 'green food'],
    "Mardi Gras": ['mardi gras', 'fat tuesday', 'king cake', 'gumbo', 'jambalaya', 'etouffee', 'beignets', 'crawfish boil', 'shrimp', 'oysters', 'muffuletta', 'pralines', 'hurricane cocktail', 'sazerac', 'cajun', 'creole', 'new orleans', 'dirty rice', 'boudin', 'andouille sausage'],
    "Cinco de Mayo": ['cinco de mayo', 'mexican food', 'tacos', 'guacamole', 'salsa', 'queso', 'margarita', 'tequila', 'cerveza', 'corona', 'enchiladas', 'fajitas', 'burritos', 'carnitas', 'al pastor', 'elote', 'mexican street corn', 'churros', 'horchata', 'jalapeno', 'cilantro', 'lime', 'fiesta'],
    "Pride Month": ['pride month', 'pride', 'rainbow', 'rainbow cake', 'rainbow cookies', 'rainbow bagel', 'colorful', 'vibrant', 'funfetti', 'sprinkles', 'fruit salad', 'skittles', 'layer cake', 'jello shots', 'cocktail', 'celebration'], 
    "Lunar New Year": ['lunar new year', 'chinese new year', 'spring festival', 'dumplings', 'jiaozi', 'potstickers', 'fish', 'spring rolls', 'egg rolls', 'niangao', 'rice cake', 'tangyuan', 'longevity noodles', 'good luck', 'prosperity', 'reunion dinner', 'hot pot'],
    "Nowruz": ['nowruz', 'noruz', 'persian new year', 'haft-seen', 'sabzi polo ba mahi', 'herbed rice', 'fish', 'kuku sabzi', 'ash reshteh', 'reshteh polo', 'dolmeh', 'samanu', 'baklava', 'persian food', 'herbs', 'spring', 'equinox'],
    "Oktoberfest": ['oktoberfest', 'german food', 'pretzel', 'soft pretzel', 'bratwurst', 'sausage', 'schnitzel', 'sauerkraut', 'german potato salad', 'kartoffelsalat', 'spaetzle', 'beer', 'german beer', 'beer cheese', 'apple strudel', 'black forest cake', 'bavarian', 'munich'],
    "Carnival": ['carnival', 'carnevale', 'feijoada', 'churrasco', 'pão de queijo', 'brigadeiros', 'fritters', 'beignets', 'doughnuts', 'zeppole', 'fritule', 'king cake', 'funnel cake', 'street food', 'fried chicken', 'empanadas', 'arepas', 'feast', 'celebration'],
    "Arab American Heritage Month": ['arab american heritage month', 'hummus', 'falafel', 'shawarma', 'kebab', 'kabob', 'tagine', 'couscous', 'tabbouleh', 'fattoush', 'baba ghanoush', 'dolma', 'stuffed grape leaves', 'kibbeh', 'manakeesh', 'zaatar', 'tahini', 'pita', 'labneh', 'foul medammes', 'koshari', 'mansaf', 'kabsa', 'baklava', 'kunafa', 'basbousa', 'levantine', 'maghrebi', 'khaleeji'],
    "Jewish American Heritage Month": ['jewish american heritage month', 'bagel', 'lox', 'brisket', 'matzo ball soup', 'challah', 'kugel', 'latkes', 'deli', 'pastrami', 'corned beef', 'rugelach', 'babka', 'hamentaschen', 'gefilte fish', 'blintz', 'shakshuka', 'schnitzel', 'tzimmes', 'cholent', 'ashkenazi', 'sephardic', 'mizrahi'],
    "Native American Heritage Month": ['native american heritage month', 'indigenous cuisine', 'three sisters', 'corn', 'beans', 'squash', 'fry bread', 'bannock', 'bison', 'buffalo', 'venison', 'wild rice', 'pemmican', 'salmon', 'trout', 'huckleberry', 'chokecherry', 'maple syrup', 'hominy', 'grits', 'succotash', 'wojapi', 'agave'],
    "Ganesh Chaturthi": ['ganesh chaturthi', 'vinayaka chaturthi', 'modak', 'prasad', 'prasadam', 'ladoo', 'laddu', 'motichoor ladoo', 'besan ladoo', 'karanji', 'puran poli', 'sundal', 'payasam', 'kheer', 'shrikhand', 'coconut', 'jaggery', 'rice flour'],
    "Asian American and Pacific Islander Heritage Month": ['aapi heritage month', 'asian american pacific islander', 'sushi', 'kimchi', 'pho', 'pad thai', 'curry', 'samosa', 'lumpia', 'dim sum', 'bao', 'ramen', 'bibimbap', 'adobo', 'poke', 'kalua pig', 'laulau', 'satay', 'rendang', 'biryani', 'dosa', 'dumplings', 'boba', 'bubble tea'],
    "Hispanic Heritage Month": ['hispanic heritage month', 'tacos', 'empanadas', 'arepas', 'ceviche', 'paella', 'tamales', 'pupusas', 'gallo pinto', 'ropa vieja', 'lechon asado', 'churros', 'flan', 'tres leches', 'salsa', 'guacamole', 'mofongo', 'lomo saltado', 'chimichurri', 'horchata', 'dulce de leche'],
    "Black History Month": ['black history month', 'soul food', 'fried chicken', 'collard greens', 'macaroni and cheese', 'cornbread', 'candied yams', 'gumbo', 'jambalaya', 'shrimp and grits', 'black-eyed peas', 'catfish', 'oxtail', 'jollof rice', 'jerk chicken', 'rice and peas', 'plantain', 'banana pudding', 'peach cobbler', 'sweet potato pie'],
    "Women's History Month": ['women\'s history month', 'female chef', 'family recipe', 'heirloom recipe', 'grandmother\'s recipe', 'matriarch', 'historic recipes', 'pioneer women', 'female empowerment', 'women-owned business', 'bake sale', 'potluck', 'community cookbook'],
    "Vaisakhi": ['vaisakhi', 'baisakhi', 'punjabi', 'harvest festival', 'langar', 'chole bhature', 'samosa', 'pakora', 'sarson ka saag', 'makki di roti', 'kadhi', 'kheer', 'gajar ka halwa', 'lassi', 'jalebi', 'atta', 'whole wheat', 'mango'],
    "Onam": ['onam', 'sadhya', 'onam sadhya', 'kerala', 'banana leaf', 'avial', 'thoran', 'olan', 'kalan', 'pachadi', 'kootu curry', 'sambar', 'rasam', 'parippu', 'inji curry', 'pappadam', 'payasam', 'pradhaman', 'upperi', 'sharkara varatti', 'vegetarian feast'],
    "Day of the Dead": ['day of the dead', 'día de los muertos', 'pan de muerto', 'sugar skulls', 'calaveras', 'ofrenda', 'tamales', 'mole', 'atole', 'champurrado', 'candied pumpkin', 'calabaza en tacha', 'pozole', 'hot chocolate', 'cempasuchil', 'marigold'],
    "Tet": ['tet', 'tet nguyen dan', 'vietnamese new year', 'bánh chưng', 'bánh tét', 'sticky rice cake', 'mut', 'candied fruits', 'thit kho', 'braised pork', 'gio cha', 'vietnamese sausage', 'xoi', 'sticky rice', 'canh mang', 'bamboo soup', 'nem ran', 'fried spring rolls', 'pickled onions']
}


cuisine_keywords = {
    "American": ['american', 'comfort food', 'burger', 'cheeseburger', 'hot dog', 'fried chicken', 'mac and cheese', 'macaroni and cheese', 'meatloaf', 'pot roast', 'barbecue', 'bbq', 'ribs', 'pulled pork', 'brisket', 'buffalo wings', 'clam chowder', 'gumbo', 'jambalaya', 'chili', 'cornbread', 'biscuit', 'apple pie', 'brownie', 'chocolate chip cookie', 'pancakes', 'waffles', 'thanksgiving dinner', 'casserole', 'tex-mex', 'cajun', 'creole', 'soul food', 'diner food'],
    "Mexican": ['mexican', 'taco', 'al pastor', 'carne asada', 'carnitas', 'barbacoa', 'enchilada', 'burrito', 'quesadilla', 'tamale', 'mole', 'pozole', 'chilaquiles', 'tostada', 'fajitas', 'salsa', 'pico de gallo', 'guacamole', 'queso', 'elote', 'mexican street corn', 'ceviche', 'churro', 'flan', 'tres leches', 'horchata', 'margarita', 'tequila', 'cilantro', 'lime', 'jalapeño', 'chipotle', 'habanero'],
    "Italian": ['italian', 'pasta', 'spaghetti', 'fettuccine', 'penne', 'lasagna', 'ravioli', 'gnocchi', 'carbonara', 'bolognese', 'alfredo', 'pesto', 'marinara', 'pizza', 'margherita', 'neapolitan', 'risotto', 'polenta', 'arancini', 'bruschetta', 'focaccia', 'prosciutto', 'parmesan', 'parmigiano-reggiano', 'mozzarella', 'ricotta', 'olive oil', 'basil', 'balsamic', 'minestrone', 'calamari', 'tiramisu', 'cannoli', 'panna cotta', 'gelato', 'espresso'],
    "Chinese": ['chinese', 'stir-fry', 'fried rice', 'lo mein', 'chow mein', 'dumplings', 'potstickers', 'bao', 'wonton', 'egg roll', 'spring roll', 'kung pao chicken', 'general tso\'s chicken', 'sesame chicken', 'sweet and sour pork', 'broccoli beef', 'mapo tofu', 'peking duck', 'dim sum', 'hot pot', 'congee', 'scallion pancake', 'soy sauce', 'hoisin', 'oyster sauce', 'sichuan', 'szechuan', 'cantonese', 'bok choy', 'ginger'],
    "Indian": ['indian', 'curry', 'tandoori', 'tikka masala', 'vindaloo', 'korma', 'madras', 'saag', 'paneer', 'samosa', 'pakora', 'naan', 'roti', 'chapati', 'paratha', 'dosa', 'biryani', 'dal', 'lentils', 'chana masala', 'aloo gobi', 'butter chicken', 'sambar', 'rasam', 'raita', 'chutney', 'lassi', 'garam masala', 'turmeric', 'cumin', 'cardamom', 'chai'],
    "Thai": ['thai', 'pad thai', 'drunken noodles', 'pad see ew', 'green curry', 'red curry', 'yellow curry', 'panang curry', 'massaman curry', 'tom yum', 'tom kha', 'satay', 'thai basil', 'lemongrass', 'galangal', 'kaffir lime', 'fish sauce', 'coconut milk', 'mango sticky rice', 'thai tea', 'spring rolls', 'papaya salad', 'larb', 'thai chili', 'peanut sauce'],
    "Japanese": ['japanese', 'sushi', 'sashimi', 'maki', 'nigiri', 'ramen', 'udon', 'soba', 'tempura', 'teriyaki', 'yakitori', 'katsu', 'donburi', 'onigiri', 'miso soup', 'edamame', 'gyoza', 'karaage', 'okonomiyaki', 'takoyaki', 'tonkatsu', 'seaweed', 'nori', 'wasabi', 'soy sauce', 'dashi', 'sake', 'matcha', 'mochi'],
    "French": ['french', 'baguette', 'croissant', 'crepe', 'macaron', 'éclair', 'soufflé', 'crème brûlée', 'mousse', 'coq au vin', 'boeuf bourguignon', 'ratatouille', 'quiche', 'soupe à l\'oignon', 'french onion soup', 'bouillabaisse', 'cassoulet', 'duck confit', 'foie gras', 'escargots', 'brie', 'camembert', 'roquefort', 'gruyère', 'truffle', 'butter', 'wine', 'champagne', 'bistro'],
    "Korean": ['korean', 'kimchi', 'korean barbecue', 'kbbq', 'bulgogi', 'galbi', 'bibimbap', 'gochujang', 'jjigae', 'kimchi jjigae', 'sundubu jjigae', 'doenjang', 'tteokbokki', 'japchae', 'pajeon', 'scallion pancake', 'gimbap', 'korean fried chicken', 'mandu', 'banchan', 'ssamjang', 'bulgogi', 'sesame oil', 'soju', 'makgeolli'],
    "Vietnamese": ['vietnamese', 'pho', 'banh mi', 'bun cha', 'spring rolls', 'goi cuon', 'summer rolls', 'egg rolls', 'cha gio', 'nuoc cham', 'fish sauce', 'com tam', 'broken rice', 'bo luc lac', 'shaking beef', 'bun bo hue', 'cao lau', 'vietnamese coffee', 'ca phe sua da', 'lemongrass', 'mint', 'cilantro', 'thai basil', 'hoisin'],
    "Middle Eastern": ['middle eastern', 'hummus', 'falafel', 'shawarma', 'kebab', 'shish kebab', 'kofta', 'tagine', 'couscous', 'tabbouleh', 'fattoush', 'baba ghanoush', 'dolma', 'stuffed grape leaves', 'kibbeh', 'manakeesh', 'pita', 'labneh', 'zaatar', 'tahini', 'sumac', 'pomegranate molasses', 'baklava', 'kunafa', 'persian', 'levantine', 'arabic'],
    "Mediterranean": ['mediterranean', 'mediterranean diet', 'olive oil', 'lemon', 'hummus', 'falafel', 'pita', 'feta', 'chickpeas', 'lentils', 'cucumber', 'tomato', 'bell pepper', 'eggplant', 'artichoke', 'couscous', 'quinoa', 'tabbouleh', 'tzatziki', 'gyro', 'souvlaki', 'grilled fish', 'salmon', 'tahini', 'oregano', 'rosemary'],
    "Greek": ['greek', 'gyro', 'souvlaki', 'moussaka', 'pastitsio', 'spanakopita', 'tiropita', 'horiatiki', 'greek salad', 'feta', 'kalamata olives', 'tzatziki', 'dolmades', 'stuffed grape leaves', 'avgolemono', 'calamari', 'octopus', 'psari plaki', 'baklava', 'galaktoboureko', 'loukoumades', 'ouzo', 'oregano', 'lemon'],
    "Spanish": ['spanish', 'tapas', 'paella', 'jamón', 'jamon iberico', 'chorizo', 'gazpacho', 'tortilla española', 'patatas bravas', 'gambas al ajillo', 'croquetas', 'manchego cheese', 'sangria', 'churros', 'crema catalana', 'pisto', 'pulpo a la gallega', 'seafood', 'saffron', 'paprika', 'pimentón', 'sherry', 'cava'],
    "Caribbean": ['caribbean', 'jerk chicken', 'jamaican', 'rice and peas', 'plantain', 'roti', 'curry goat', 'oxtail', 'ackee and saltfish', 'callaloo', 'cuban sandwich', 'ropa vieja', 'mofongo', 'lechon asado', 'tostones', 'arroz con pollo', 'jerk seasoning', 'allspice', 'scotch bonnet', 'mango', 'coconut', 'rum', 'mojito', 'piña colada'],
    "German": ['german', 'schnitzel', 'bratwurst', 'wurst', 'sauerkraut', 'pretzel', 'spaetzle', 'kartoffelsalat', 'german potato salad', 'sauerbraten', 'rouladen', 'currywurst', 'leberkäse', 'kasespatzle', 'black forest cake', 'strudel', 'stollen', 'pumpernickel', 'rye bread', 'mustard', 'beer', 'riesling', 'bavarian'],
    "Brazilian": ['brazilian', 'feijoada', 'churrasco', 'picanha', 'pão de queijo', 'coxinha', 'acarajé', 'moqueca', 'farofa', 'pastel', 'brigadeiro', 'açaí', 'caipirinha', 'cachaça', 'guarana', 'passion fruit', 'mango', 'cassava', 'yuca', 'brazil nut'],
    "Turkish": ['turkish', 'kebab', 'döner kebab', 'shish kebab', 'adana kebab', 'iskender kebab', 'köfte', 'pide', 'lahmacun', 'meze', 'dolma', 'sarma', 'borek', 'simit', 'menemen', 'lentil soup', 'mercimek çorbası', 'pilaf', 'yogurt', 'eggplant', 'baklava', 'künefe', 'lokum', 'turkish delight', 'turkish coffee', 'ayran', 'raki'],
    "Russian": ['russian', 'borscht', 'beef stroganoff', 'pelmeni', 'vareniki', 'blini', 'syrniki', 'cabbage rolls', 'golubtsy', 'solyanka', 'okroshka', 'shchi', 'olivier salad', 'herring under a fur coat', 'zakuski', 'kasha', 'kvass', 'rye bread', 'caviar', 'sour cream', 'smetana', 'dill', 'tvorog'],
    "Ethiopian": ['ethiopian', 'injera', 'wat', 'wot', 'doro wat', 'misir wot', 'kitfo', 'tibs', 'gomen', 'shiro', 'berbere', 'niter kibbeh', 'ayib', 'ethiopian coffee', 'tej', 'honey wine', 'teff', 'lentils', 'collard greens', 'communal dining'],
    "Moroccan": ['moroccan', 'tagine', 'tajine', 'couscous', 'pastilla', 'bisteeya', 'harira', 'ras el hanout', 'kefta', 'kofta', 'mechoui', 'zalouk', 'shakshuka', 'preserved lemons', 'argan oil', 'mint tea', 'harissa', 'saffron', 'apricots', 'almonds', 'dates', 'chebakia'],
    "British": ['british', 'english', 'fish and chips', 'sunday roast', 'roast beef', 'yorkshire pudding', 'shepherd\'s pie', 'cottage pie', 'bangers and mash', 'full english breakfast', 'toad in the hole', 'ploughman\'s lunch', 'cornish pasty', 'beef wellington', 'scotch egg', 'scones', 'clotted cream', 'sticky toffee pudding', 'trifle', 'eton mess', 'crumble', 'custard', 'tea', 'cheddar'],
    "Polish": ['polish', 'pierogi', 'kielbasa', 'gołąbki', 'cabbage rolls', 'bigos', 'hunter\'s stew', 'żurek', 'barszcz', 'borscht', 'kotlet schabowy', 'placki ziemniaczane', 'potato pancakes', 'zapiekanka', 'kopytka', 'pączki', 'makowiec', 'sernik', 'sauerkraut', 'sour cream', 'poppy seed', 'oscypek'],
    "Jewish": ['jewish', 'challah', 'matzo ball soup', 'brisket', 'gefilte fish', 'kugel', 'latke', 'bagel', 'lox', 'deli', 'pastrami', 'shakshuka', 'falafel', 'sabich', 'schnitzel', 'hummus', 'cholent', 'tzimmes', 'rugelach', 'babka', 'hamentaschen', 'ashkenazi', 'sephardic', 'kosher'],
    "Filipino": ['filipino', 'adobo', 'sinigang', 'lechon', 'lumpia', 'pancit', 'crispy pata', 'kare-kare', 'sisig', 'longganisa', 'tapsilog', 'arroz caldo', 'bibingka', 'puto', 'ube', 'halo-halo', 'leche flan', 'calamansi', 'patis', 'fish sauce', 'vinegar', 'soy sauce', 'bagoong'],
    "Peruvian": ['peruvian', 'ceviche', 'cebiche', 'lomo saltado', 'aji de gallina', 'pollo a la brasa', 'causa rellena', 'anticuchos', 'rocoto relleno', 'papas a la huancaina', 'arroz con pollo', 'seco de carne', 'chifa', 'nikkei', 'leche de tigre', 'pisco sour', 'chicha morada', 'inca kola', 'aji amarillo', 'quinoa', 'andean'],
    "Argentinian": ['argentinian', 'asado', 'parrillada', 'steak', 'bife de chorizo', 'chimichurri', 'empanadas', 'milanesa', 'provoleta', 'choripán', 'matambre arrollado', 'locro', 'humita', 'dulce de leche', 'alfajores', 'yerba mate', 'mate', 'malbec', 'patagonian', 'gaucho'],
    "Pakistani": ['pakistani', 'nihari', 'haleem', 'biryani', 'pulao', 'karahi', 'korma', 'chicken tikka', 'seekh kebab', 'shami kebab', 'chapli kebab', 'naan', 'roti', 'paratha', 'dal', 'chana masala', 'halwa puri', 'samosa', 'raita', 'lassi', 'falooda', 'kheer', 'gajar ka halwa', 'peshawari', 'lahori', 'mughlai'],
    "Cajun": ['cajun', 'gumbo', 'jambalaya', 'étouffée', 'etouffee', 'crawfish boil', 'boudin', 'andouille', 'tasso ham', 'dirty rice', 'rice and gravy', 'holy trinity', 'roux', 'blackened', 'alligator', 'catfish', 'cayenne', 'bayou', 'louisiana'],
    "Creole": ['creole', 'shrimp creole', 'gumbo', 'red beans and rice', 'jambalaya', 'grillades and grits', 'oysters rockefeller', 'turtle soup', 'pain perdu', 'bananas foster', 'pralines', 'beignets', 'sazerac', 'remoulade', 'new orleans', 'louisiana'],
    "Tex-Mex": ['tex-mex', 'fajitas', 'nachos', 'chili con carne', 'queso', 'queso dip', 'chimichanga', 'hard shell taco', 'ground beef', 'frijoles', 'refried beans', 'flour tortilla', 'king ranch casserole', 'breakfast burrito', 'margarita', 'cumin', 'cheddar cheese'],
    "Californian": ['californian', 'california cuisine', 'farm-to-table', 'avocado toast', 'sourdough', 'cobb salad', 'cioppino', 'fusion taco', 'fish taco', 'sushi roll', 'california roll', 'tri-tip', 'artichoke', 'kale', 'quinoa', 'almonds', 'napa valley', 'sonoma'],
    "New England": ['new england', 'clam chowder', 'lobster roll', 'steamed lobster', 'fried clams', 'cod', 'haddock', 'scallops', 'oysters', 'boston baked beans', 'brown bread', 'pot roast', 'clam bake', 'indian pudding', 'whoopie pie', 'boston cream pie', 'apple cider donuts', 'maple syrup', 'vermont', 'maine'],
    "Hawaiian": ['hawaiian', 'poke', 'kalua pig', 'laulau', 'poi', 'lomi-lomi salmon', 'haupia', 'luau', 'plate lunch', 'macaroni salad', 'spam musubi', 'loco moco', 'shave ice', 'manapua', 'huli huli chicken', 'saimin', 'taro', 'pineapple'],
    "Amish": ['amish', 'pennsylvania dutch', 'shoofly pie', 'whoopie pie', 'chicken pot pie', 'scrapple', 'apple butter', 'chow-chow', 'pot roast', 'beef and noodles', 'ham loaf', 'pretzels', 'funnel cake', 'rhubarb', 'casserole', 'dumplings', 'preserves', 'canning'],
    "Soul Food": ['soul food', 'fried chicken', 'collard greens', 'macaroni and cheese', 'mac & cheese', 'cornbread', 'candied yams', 'sweet potatoes', 'black-eyed peas', 'grits', 'shrimp and grits', 'fried catfish', 'chitterlings', 'chitlins', 'oxtail', 'hog maws', 'ham hocks', 'neckbones', 'banana pudding', 'peach cobbler', 'sweet potato pie', 'sweet tea'],
    "Barbecue": ['barbecue', 'bbq', 'barbeque', 'brisket', 'pulled pork', 'pork shoulder', 'ribs', 'baby back ribs', 'st. louis style ribs', 'burnt ends', 'smoked sausage', 'bbq chicken', 'texas barbecue', 'kansas city barbecue', 'carolina barbecue', 'memphis barbecue', 'vinegar sauce', 'mustard sauce', 'sweet sauce', 'dry rub', 'wet rub', 'smoker', 'low and slow'],
    "Appalachian": ['appalachian', 'cornbread', 'beans and cornbread', 'soup beans', 'pinto beans', 'biscuits and gravy', 'fried chicken', 'cathead biscuits', 'stack cake', 'ramps', 'morels', 'pawpaw', 'hickory nuts', 'venison', 'squirrel', 'dumplings', 'chow-chow', 'apple butter', 'molasses', 'shucky beans', 'leather britches', 'cast iron']
}




diet_keywords = {
    "Vegetarian": ['vegetarian', 'veggie', 'meatless', 'meat-free', 'plant-based', 'legume', 'lentil', 'beans', 'chickpeas', 'tofu', 'tempeh', 'seitan', 'edamame', 'quinoa', 'vegetable', 'fruit', 'mushrooms', 'plant-forward', 'lacto-ovo', 'no meat'],
    "Vegan": ['vegan', 'plant-based', 'meatless', 'dairy-free', 'egg-free', 'no animal products', 'tofu', 'tempeh', 'seitan', 'lentil', 'legume', 'nutritional yeast', 'nooch', 'aquafaba', 'flax egg', 'cashew cream', 'plant milk', 'almond milk', 'soy milk', 'oat milk', 'vegan cheese', 'plant-forward'],
    "Gluten-Free": ['gluten-free', 'gf', 'celiac', 'no gluten', 'no wheat', 'gluten-free flour', 'almond flour', 'coconut flour', 'tapioca starch', 'rice flour', 'quinoa', 'rice', 'corn', 'buckwheat', 'millet', 'amaranth', 'sorghum', 'gluten-free oats', 'cauliflower crust', 'zucchini noodles', 'zoodles'],
    "Keto": ['keto', 'ketogenic', 'low-carb', 'lchf', 'high-fat', 'net carbs', 'fat bomb', 'ketosis', 'bacon', 'avocado', 'mct oil', 'coconut oil', 'almond flour', 'cauliflower rice', 'zucchini noodles', 'erythritol', 'monk fruit', 'stevia', 'no sugar', 'no grains'],
    "Paleo": ['paleo', 'paleolithic', 'primal', 'caveman diet', 'whole foods', 'unprocessed', 'no grains', 'no legumes', 'no dairy', 'no refined sugar', 'hunter-gatherer', 'lean meat', 'grass-fed', 'wild-caught', 'nuts', 'seeds', 'sweet potato', 'almond flour', 'coconut flour', 'ghee'],
    "Low-Carb": ['low-carb', 'low-carbohydrate', 'lchf', 'keto-friendly', 'atkins', 'no sugar', 'no grains', 'no bread', 'no pasta', 'cauliflower rice', 'zucchini noodles', 'lettuce wrap', 'protein style', 'lean protein', 'healthy fats', 'non-starchy vegetables', 'berries'],
    "High-Protein": ['high-protein', 'protein-rich', 'protein-packed', 'macros', 'lean protein', 'muscle building', 'post-workout', 'chicken breast', 'turkey', 'lean beef', 'fish', 'tuna', 'salmon', 'eggs', 'egg whites', 'greek yogurt', 'cottage cheese', 'whey protein', 'casein', 'protein powder', 'tofu', 'edamame', 'lentils', 'beans'],
    "Pescatarian": ['pescatarian', 'pescetarian', 'seafood', 'fish', 'shellfish', 'shrimp', 'scallops', 'salmon', 'tuna', 'cod', 'sardines', 'mackerel', 'no meat', 'meatless', 'plant-based with fish'],
    "Dairy-Free": ['dairy-free', 'no dairy', 'lactose-free', 'casein-free', 'plant milk', 'almond milk', 'oat milk', 'soy milk', 'coconut milk', 'cashew milk', 'rice milk', 'vegan butter', 'margarine', 'ghee', 'coconut yogurt', 'nutritional yeast', 'vegan cheese'],
    "Nut-Free": ['nut-free', 'no nuts', 'nut allergy', 'peanut-free', 'tree nut free', 'sunflower seeds', 'pumpkin seeds', 'sesame seeds', 'tahini', 'sunflower seed butter', 'seed butter', 'allergy-friendly'],
    "Soy-Free": ['soy-free', 'no soy', 'soy allergy', 'coconut aminos', 'tamari-free', 'tofu-free', 'edamame-free', 'soy milk free', 'chickpeas', 'lentils', 'beans', 'seitan'],
    "Sugar-Free": ['sugar-free', 'no sugar', 'no added sugar', 'refined sugar free', 'unsweetened', 'low glycemic', 'diabetic-friendly', 'stevia', 'monk fruit', 'erythritol', 'xylitol', 'yacon syrup', 'allulose', 'natural sweetener'],
    "Halal": ['halal', 'zabihah', 'islamic law', 'no pork', 'no alcohol', 'halal meat', 'halal certified', 'dhabiha', 'tayyib'],
    "Kosher": ['kosher', 'kashrut', 'pareve', 'parve', 'fleishig', 'milchig', 'kosher salt', 'no pork', 'no shellfish', 'kosher certified', 'hechsher', 'ou', 'star-k', 'ok'],
    "Low-Sodium": ['low-sodium', 'low-salt', 'no salt', 'no salt added', 'salt-free', 'dash diet', 'heart-healthy', 'herbs', 'spices', 'mrs. dash', 'vinegar', 'citrus', 'lemon juice', 'potassium chloride'],
    "Diabetic-Friendly": ['diabetic-friendly', 'diabetic diet', 'low glycemic', 'low gi', 'controlled carbohydrate', 'sugar-free', 'no added sugar', 'whole grains', 'lean protein', 'non-starchy vegetables', 'healthy fats', 'fiber-rich', 'portion control'],
    "Raw Food": ['raw food', 'raw diet', 'raw vegan', 'uncooked', 'unprocessed', 'no-bake', 'living foods', 'dehydrated', 'sprouted', 'cold-pressed', 'juicing', 'smoothie', 'zoodles', 'kelp noodles', 'raw nuts', 'raw seeds', 'fresh fruit', 'fresh vegetables']
}


region_keywords = {
    "Southern": ['southern', 'fried chicken', 'biscuits', 'gravy', 'grits', 'shrimp and grits', 'collard greens', 'macaroni and cheese', 'cornbread', 'fried green tomatoes', 'pecan pie', 'sweet potato pie', 'banana pudding', 'peach cobbler', 'sweet tea', 'pimento cheese', 'deviled eggs', 'hushpuppies', 'catfish', 'country ham', 'pulled pork', 'lowcountry', 'soul food', 'appalachian', 'cajun', 'creole'],
    "Midwestern": ['midwestern', 'casserole', 'hotdish', 'pot roast', 'pork tenderloin sandwich', 'loose meat sandwich', 'jucy lucy', 'bratwurst', 'cheese curds', 'cincinnati chili', 'chicago style hot dog', 'deep dish pizza', 'corn on the cob', 'puppy chow', 'buckeye candy', 'gooey butter cake', 'fruit pie', 'ambrosia salad', 'jell-o salad', 'ranch dressing', 'beer cheese soup'],
    "Pacific Northwest": ['pacific northwest', 'pnw', 'salmon', 'smoked salmon', 'cedar plank salmon', 'dungeness crab', 'oysters', 'geoduck', 'clams', 'halibut', 'foraged mushrooms', 'chanterelles', 'truffles', 'berries', 'marionberry', 'huckleberry', 'hazelnuts', 'coffee', 'craft beer', 'ipa', 'dutch baby pancake', 'teriyaki', 'rainier cherries'],
    "Northeast": ['northeast', 'new england', 'mid-atlantic', 'clam chowder', 'lobster roll', 'crab cakes', 'steamed clams', 'fried clams', 'oysters', 'cod', 'scallops', 'cheesesteak', 'philly cheesesteak', 'hoagie', 'pizza', 'new york style pizza', 'bagel', 'lox', 'deli sandwich', 'pastrami', 'reuben', 'buffalo wings', 'salt potatoes', 'whoopie pie', 'boston cream pie', 'apple cider', 'maple syrup'],
    "West": ['west', 'western', 'farm-to-table', 'californian', 'avocado', 'sourdough', 'tri-tip', 'cioppino', 'fish taco', 'fusion', 'rocky mountain oysters', 'bison', 'elk', 'trout', 'huckleberry', 'finger steaks', 'ranch cooking', 'dutch oven', 'cowboy beans', 'sourdough starter'],
    "Southwest": ['southwest', 'southwestern', 'new mexican', 'chile', 'chili pepper', 'hatch chiles', 'red chile', 'green chile', 'enchiladas', 'posole', 'pozole', 'carne adovada', 'fajitas', 'navajo taco', 'fry bread', 'sopapillas', 'biscochitos', 'pinto beans', 'prickly pear', 'mesquite', 'sonoran', 'tex-mex'],
    "North": ['north', 'upper midwest', 'great lakes', 'fish fry', 'walleye', 'perch', 'trout', 'smoked fish', 'wild rice', 'wild rice soup', 'pasties', 'bratwurst', 'kielbasa', 'cheese curds', 'beer cheese soup', 'hotdish', 'lefse', 'krumkake', 'dane county farmers market', 'door county', 'cherry pie', 'venison']
}

course_keywords = {
    "Appetizer": ['appetizer', 'starter', 'snack', 'finger food', 'hors d\'oeuvre', 'amuse-bouche', 'canapé', 'nibbles', 'small bites', 'first course', 'pre-dinner', 'munchies', 'tidbits', 'dip', 'spread', 'bruschetta', 'crostini', 'tapas', 'meze', 'antipasto', 'charcuterie board', 'cheese board', 'skewer', 'pinwheel', 'puff pastry', 'spring roll', 'egg roll', 'samosa', 'pakora', 'dumpling', 'gyoza', 'potsticker', 'quesadilla', 'taquito', 'deviled eggs', 'stuffed mushrooms', 'shrimp cocktail', 'wings', 'sliders', 'nachos', 'jalapeño poppers', 'mozzarella sticks', 'fritter', 'relish tray', 'crudités', 'shareable', 'party food', 'bite-sized', 'small plate', 'pâté'],
    "Main Course": ['main course', 'main dish', 'entrée', 'entree', 'main', 'principal dish', 'dinner', 'supper', 'family meal', 'centerpiece', 'roast', 'casserole', 'stew', 'curry', 'steak', 'chops', 'cutlet', 'stir-fry', 'pasta', 'noodles', 'savory pie', 'pot pie', 'shepherd\'s pie', 'platter', 'board', 'skillet meal', 'one-pot meal', 'one-pan meal', 'meatloaf', 'burger', 'sandwich', 'wrap', 'bowl', 'grain bowl', 'hearty soup', 'chowder', 'lasagna', 'enchiladas', 'fajitas', 'tacos', 'burrito', 'pizza', 'flatbread', 'gratin', 'roulade', 'meatballs', 'schnitzel', 'fish fillet', 'roast chicken', 'prime rib'],
    "Side Dish": ['side dish', 'side', 'accompaniment', 'side order', 'on the side', 'complement', 'extra', 'garnish', 'salad', 'green salad', 'pasta salad', 'potato salad', 'coleslaw', 'slaw', 'vegetable', 'steamed vegetables', 'roasted vegetables', 'grilled vegetables', 'sautéed vegetables', 'glazed vegetables', 'creamed vegetables', 'potatoes', 'mashed potatoes', 'roasted potatoes', 'scalloped potatoes', 'au gratin', 'fries', 'french fries', 'rice', 'pilaf', 'fried rice', 'couscous', 'quinoa', 'grains', 'risotto', 'polenta', 'beans', 'baked beans', 'refried beans', 'lentils', 'dal', 'stuffing', 'dressing', 'relish', 'chutney', 'salsa', 'bread', 'dinner rolls', 'biscuits', 'cornbread', 'garlic bread'],
    "Dessert": ['dessert', 'sweet', 'pudding', 'afters', 'confection', 'sweet treat', 'final course', 'cake', 'cupcake', 'cheesecake', 'lava cake', 'torte', 'pie', 'tart', 'cookies', 'brownies', 'blondies', 'bars', 'ice cream', 'gelato', 'sorbet', 'sherbet', 'frozen yogurt', 'mousse', 'custard', 'crème brûlée', 'panna cotta', 'cobbler', 'crumble', 'crisp', 'clafoutis', 'trifle', 'pastry', 'éclair', 'macaron', 'donut', 'fritter', 'fudge', 'candy', 'truffles', 'bonbon', 'fruit', 'fruit salad', 'parfait', 'sundae', 'semifreddo', 'soufflé', 'meringue'],
    "Drink": ['drink', 'beverage', 'libation', 'refreshment', 'cocktail', 'mocktail', 'smoothie', 'shake', 'milkshake', 'juice', 'lemonade', 'limeade', 'ade', 'iced tea', 'sweet tea', 'coffee', 'latte', 'cappuccino', 'espresso', 'macchiato', 'mocha', 'cold brew', 'hot chocolate', 'cocoa', 'soda', 'pop', 'fizz', 'punch', 'spritzer', 'shrub', 'agua fresca', 'horchata', 'lassi', 'chai', 'kombucha', 'tisane', 'herbal tea', 'water', 'sparkling water', 'wine', 'red wine', 'white wine', 'rosé', 'beer', 'ale', 'lager', 'spirits', 'liquor', 'liqueur']
}


tags_to_insert = {
    "holiday": list(holiday_keywords.keys()),
    "diet": list(diet_keywords.keys()),
    "cuisine": list(cuisine_keywords.keys()),
    "region": list(region_keywords.keys()),
    "course": list(course_keywords.keys())
}


# insert tags into the database
def bulk_insert_tags():
    with engine.begin() as conn:
        inserts = []

        for tag_type, tag_names in tags_to_insert.items():
            for name in tag_names:
                inserts.append({"name": name, "type": tag_type})

        if inserts:
            conn.execute(
                text(f"""
                    INSERT INTO {DB_NAME}.tags (tag_name, tag_type)
                    VALUES (:name, :type)
                    ON CONFLICT DO NOTHING
                """),
                inserts
            )

    print("Tags inserted into tags table.")


# insert keywords into tag_keywords table
def get_all_tag_ids(conn):
    tag_ids = conn.execute(text(f"SELECT tag_id, tag_name, tag_type FROM {DB_NAME}.tags")).mappings()
    tag_lookup = defaultdict(dict)
    for row in tag_ids:
        tag_lookup[row["tag_type"]][row["tag_name"]] = row["tag_id"]
    return tag_lookup


def bulk_insert_keywords():
    print("Inserting tags into tags table...")
    bulk_insert_tags()
    print("Inserting keywords into tag_keywords...")
    with engine.begin() as conn:
        tag_lookup = get_all_tag_ids(conn)

        inserts = []

        for tag_type, tag_dict in [
            ("holiday", holiday_keywords),
            ("cuisine", cuisine_keywords),
            ("diet", diet_keywords),
            ("region", region_keywords),
            ("course", course_keywords)
        ]:
            for tag_name, keywords in tag_dict.items():
                tag_id = tag_lookup.get(tag_type, {}).get(tag_name)
                if not tag_id:
                    print(f"Tag '{tag_name}' with type '{tag_type}' not found in tags table.")
                    continue

                for keyword in keywords:
                    inserts.append({"tag_id": tag_id, "keyword": keyword})

        if inserts:
            conn.execute(
                text(f"""
                    INSERT INTO {DB_NAME}.tag_keywords (tag_id, keyword)
                    VALUES (:tag_id, :keyword)
                    ON CONFLICT DO NOTHING
                """),
                inserts
            )

    print("Keywords inserted into tag_keywords.")



def fetch_all_tag_keywords(conn):
    result = conn.execute(text(f"SELECT tag_id, keyword FROM {DB_NAME}.tag_keywords")).mappings()

    tag_map = {}
    for row in result:
        tag_id = row['tag_id']
        keyword = row['keyword'].lower()
        if tag_id not in tag_map:
            tag_map[tag_id] = set()
        tag_map[tag_id].add(keyword)

    return tag_map


def fetch_all_recipes(conn):
    result = conn.execute(text(f"SELECT recipe_id, recipe_name, instructions FROM {DB_NAME}.recipe")).mappings()
    return result.fetchall()


def tag_recipe(conn, recipe_id, tag_id):
    exists = conn.execute(text(f"""
        SELECT 1 FROM {DB_NAME}.recipe_tags_mapping WHERE recipe_id = :rid AND tag_id = :tid
    """), {"rid": recipe_id, "tid": tag_id}).first()
    
    if not exists:
        conn.execute(text(f"""
            INSERT INTO {DB_NAME}.recipe_tags_mapping (recipe_id, tag_id) VALUES (:rid, :tid)
        """), {"rid": recipe_id, "tid": tag_id})
    

def auto_tag_recipes():
    print("Auto-tagging recipes based on keywords...")
    with engine.begin() as conn:
        tag_map = fetch_all_tag_keywords(conn)
        recipes = fetch_all_recipes(conn)

        bulk_insert_list = []

        for recipe in recipes:
            content = f"{recipe['recipe_name']} {recipe['instructions']}".lower()
            for tag_id, keywords in tag_map.items():
                if any(kw in content for kw in keywords):
                    bulk_insert_list.append({
                        "rid": recipe["recipe_id"],
                        "tid": tag_id
                    })

        if bulk_insert_list:
            conn.execute(
                text(f"""
                    INSERT INTO {DB_NAME}.recipe_tags_mapping (recipe_id, tag_id)
                    VALUES (:rid, :tid)
                    ON CONFLICT DO NOTHING
                """),
                bulk_insert_list
            )

    print("Recipes auto-tagged based on keywords.")


def tag_recipe_by_id(recipe_id):
    with engine.begin() as conn:
        tag_map = fetch_all_tag_keywords(conn)
        recipe = conn.execute(text(f"SELECT recipe_name, instructions FROM {DB_NAME}.recipe WHERE recipe_id = :rid"),
                              {"rid": recipe_id}).fetchone()
        
        if not recipe:
            print(f"Recipe with ID {recipe_id} not found.")
            return
        
        content = f"{recipe['recipe_name']} {recipe['instructions']}".lower()
        
        for tag_id, keywords in tag_map.items():
            if any(kw in content for kw in keywords):
                tag_recipe(conn, recipe_id, tag_id)
    print(f"Recipe {recipe_id} auto-tagged based on keywords.")
