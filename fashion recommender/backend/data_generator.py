"""
Generates a structured, diverse, realistic dataset of 1,000+ fashion products
covering Male, Female, and Unisex across all 27 Occasions, 26+ Colors, 20 Aesthetics,
18 Fabrics, 8 Fits, Sleeve Lengths, Garment Lengths, and Body Shape/Skin Tone compatibilities.
"""

import json
import random
import os

OCCASIONS = [
    "College", "University", "Office", "Business Meeting", "Interview",
    "Casual Outing", "Shopping", "Travel", "Vacation", "Party",
    "Birthday", "Date", "Dinner", "Wedding", "Engagement",
    "Festival", "Religious Event", "Family Gathering", "Brunch", "Beach",
    "Sports", "Gym", "Concert", "Formal Event", "Semi-Formal Event",
    "Photoshoot", "Other / Custom Occasion"
]

COLOR_FAMILIES = {
    "Black": "Black",
    "White": "Neutral",
    "Grey": "Neutral",
    "Navy": "Blue",
    "Blue": "Blue",
    "Sky Blue": "Blue",
    "Red": "Red",
    "Maroon": "Red",
    "Pink": "Pink",
    "Rose": "Pink",
    "Purple": "Purple",
    "Lavender": "Purple",
    "Green": "Green",
    "Olive": "Green",
    "Emerald": "Green",
    "Yellow": "Yellow",
    "Mustard": "Yellow",
    "Orange": "Orange",
    "Brown": "Earth",
    "Beige": "Neutral",
    "Cream": "Neutral",
    "Tan": "Earth",
    "Khaki": "Earth",
    "Burgundy": "Red",
    "Teal": "Blue",
    "Turquoise": "Blue",
    # Custom shades mapping
    "Sage Green": "Green",
    "Terracotta": "Earth",
    "Peach": "Pink",
    "Coral": "Pink",
    "Wine": "Red",
    "Dusty Pink": "Pink",
    "Champagne": "Neutral",
    "Mint Green": "Green",
    "Lilac": "Purple"
}

AESTHETICS = [
    "Casual", "Formal", "Semi-formal", "Smart Casual", "Streetwear",
    "Minimal", "Oversized", "Elegant", "Traditional", "Ethnic",
    "Western", "Sporty", "Vintage", "Y2K", "Trendy",
    "Classic", "Luxury", "Bohemian", "Preppy", "Athleisure"
]

FABRICS = [
    "Cotton", "Linen", "Denim", "Wool", "Silk", "Polyester", "Leather",
    "Rayon", "Chiffon", "Georgette", "Satin", "Velvet", "Crepe",
    "Organza", "Khadi", "Modal", "Knit", "Jersey"
]

FITS = [
    "Slim Fit", "Regular Fit", "Relaxed Fit", "Oversized", "Loose Fit",
    "Tailored Fit", "Bodycon Fit", "Straight Fit"
]

SLEEVE_LENGTHS = [
    "Sleeveless", "Cap Sleeve", "Half Sleeve", "Three-Quarter Sleeve",
    "Full Sleeve", "Adjustable / Variable"
]

GARMENT_LENGTHS = [
    "Cropped", "Short", "Standard", "Long", "Maxi", "Ankle Length", "Floor Length"
]

BODY_SHAPES = ["Hourglass", "Rectangle", "Pear / Triangle", "Inverted Triangle", "Apple", "All"]
SKIN_TONES = ["Warm", "Cool", "Neutral", "Fair", "Medium", "Deep", "All"]

# Curated High-Definition Unsplash Fashion Images by Category
IMAGE_MAP = {
    # Female Traditional
    "Sarees": [
        "https://images.unsplash.com/photo-1610030469983-98e550d6193c?w=600&auto=format&fit=crop&q=80",
        "https://images.unsplash.com/photo-1617627143750-d86bc21e42bb?w=600&auto=format&fit=crop&q=80",
        "https://images.unsplash.com/photo-1583391733956-3750e0ff4e8b?w=600&auto=format&fit=crop&q=80"
    ],
    "Designer sarees": [
        "https://images.unsplash.com/photo-1610030469983-98e550d6193c?w=600&auto=format&fit=crop&q=80",
        "https://images.unsplash.com/photo-1617627143750-d86bc21e42bb?w=600&auto=format&fit=crop&q=80"
    ],
    "Lehengas": [
        "https://images.unsplash.com/photo-1594744803329-e58b31de8bf5?w=600&auto=format&fit=crop&q=80",
        "https://images.unsplash.com/photo-1583391733956-3750e0ff4e8b?w=600&auto=format&fit=crop&q=80"
    ],
    "Anarkali suits": [
        "https://images.unsplash.com/photo-1583391733956-3750e0ff4e8b?w=600&auto=format&fit=crop&q=80",
        "https://images.unsplash.com/photo-1610030469983-98e550d6193c?w=600&auto=format&fit=crop&q=80"
    ],
    "Salwar suits": [
        "https://images.unsplash.com/photo-1609357605129-26f69add5d6e?w=600&auto=format&fit=crop&q=80",
        "https://images.unsplash.com/photo-1617627143750-d86bc21e42bb?w=600&auto=format&fit=crop&q=80"
    ],
    "Sharara sets": [
        "https://images.unsplash.com/photo-1594744803329-e58b31de8bf5?w=600&auto=format&fit=crop&q=80",
        "https://images.unsplash.com/photo-1610030469983-98e550d6193c?w=600&auto=format&fit=crop&q=80"
    ],
    "Palazzo sets": [
        "https://images.unsplash.com/photo-1583391733956-3750e0ff4e8b?w=600&auto=format&fit=crop&q=80",
        "https://images.unsplash.com/photo-1609357605129-26f69add5d6e?w=600&auto=format&fit=crop&q=80"
    ],
    "Kurtis": [
        "https://images.unsplash.com/photo-1609357605129-26f69add5d6e?w=600&auto=format&fit=crop&q=80",
        "https://images.unsplash.com/photo-1583391733956-3750e0ff4e8b?w=600&auto=format&fit=crop&q=80"
    ],
    "Ethnic gowns": [
        "https://images.unsplash.com/photo-1594744803329-e58b31de8bf5?w=600&auto=format&fit=crop&q=80"
    ],
    "Indo-western outfits": [
        "https://images.unsplash.com/photo-1583391733956-3750e0ff4e8b?w=600&auto=format&fit=crop&q=80"
    ],
    # Female Western
    "Dresses": [
        "https://images.unsplash.com/photo-1572804013309-59a88b7e92f1?w=600&auto=format&fit=crop&q=80",
        "https://images.unsplash.com/photo-1515372039744-b8f02a3ae446?w=600&auto=format&fit=crop&q=80",
        "https://images.unsplash.com/photo-1539109136881-3be0616acf4b?w=600&auto=format&fit=crop&q=80"
    ],
    "Tops": [
        "https://images.unsplash.com/photo-1534126511673-b6899657816a?w=600&auto=format&fit=crop&q=80",
        "https://images.unsplash.com/photo-1565699774381-d421d9e7ad41?w=600&auto=format&fit=crop&q=80",
        "https://images.unsplash.com/photo-1503342217505-b0a15ec3261c?w=600&auto=format&fit=crop&q=80"
    ],
    "Shirts": [
        "https://images.unsplash.com/photo-1598033129183-c4f50c736f10?w=600&auto=format&fit=crop&q=80",
        "https://images.unsplash.com/photo-1596755094514-f87e34085b2c?w=600&auto=format&fit=crop&q=80"
    ],
    "Jeans": [
        "https://images.unsplash.com/photo-1541099649105-f69ad21f3246?w=600&auto=format&fit=crop&q=80",
        "https://images.unsplash.com/photo-1582552938357-32b906df40cb?w=600&auto=format&fit=crop&q=80"
    ],
    "Trousers": [
        "https://images.unsplash.com/photo-1594633312681-425c7b97ccd1?w=600&auto=format&fit=crop&q=80",
        "https://images.unsplash.com/photo-1624378439575-d8705ad7ae80?w=600&auto=format&fit=crop&q=80"
    ],
    "Skirts": [
        "https://images.unsplash.com/photo-1583496661160-fb5886a0aaaa?w=600&auto=format&fit=crop&q=80"
    ],
    "Jumpsuits": [
        "https://images.unsplash.com/photo-1502716119720-b23a93e5fe1b?w=600&auto=format&fit=crop&q=80"
    ],
    "Blazers": [
        "https://images.unsplash.com/photo-1584273143981-41c073dfe8f8?w=600&auto=format&fit=crop&q=80",
        "https://images.unsplash.com/photo-1507679799987-c73779587ccf?w=600&auto=format&fit=crop&q=80"
    ],
    "Co-ord sets": [
        "https://images.unsplash.com/photo-1515886657613-9f3515b0c78f?w=600&auto=format&fit=crop&q=80"
    ],
    "Casual wear": [
        "https://images.unsplash.com/photo-1515886657613-9f3515b0c78f?w=600&auto=format&fit=crop&q=80",
        "https://images.unsplash.com/photo-1521572267360-ee0c2909d518?w=600&auto=format&fit=crop&q=80"
    ],
    # Female Footwear
    "Heels": [
        "https://images.unsplash.com/photo-1543163521-1bf539c55dd2?w=600&auto=format&fit=crop&q=80",
        "https://images.unsplash.com/photo-1535043934128-cf0b28d52f95?w=600&auto=format&fit=crop&q=80"
    ],
    "Flats": [
        "https://images.unsplash.com/photo-1562273138-f46be4ebdf33?w=600&auto=format&fit=crop&q=80"
    ],
    "Sandals": [
        "https://images.unsplash.com/photo-1603808033192-082d6919d3e1?w=600&auto=format&fit=crop&q=80"
    ],
    "Ethnic footwear": [
        "https://images.unsplash.com/photo-1543163521-1bf539c55dd2?w=600&auto=format&fit=crop&q=80",
        "https://images.unsplash.com/photo-1562273138-f46be4ebdf33?w=600&auto=format&fit=crop&q=80"
    ],
    "Sneakers": [
        "https://images.unsplash.com/photo-1595950653106-6c9ebd614d3a?w=600&auto=format&fit=crop&q=80",
        "https://images.unsplash.com/photo-1552346154-21d32810aba3?w=600&auto=format&fit=crop&q=80"
    ],
    "Boots": [
        "https://images.unsplash.com/photo-1608256246200-53e635b5b65f?w=600&auto=format&fit=crop&q=80"
    ],
    # Female Accessories
    "Handbags": [
        "https://images.unsplash.com/photo-1584917865442-de89df76afd3?w=600&auto=format&fit=crop&q=80"
    ],
    "Clutches": [
        "https://images.unsplash.com/photo-1566150905458-1bf1fc113f0d?w=600&auto=format&fit=crop&q=80"
    ],
    "Earrings": [
        "https://images.unsplash.com/photo-1630019852942-f89202989a59?w=600&auto=format&fit=crop&q=80"
    ],
    "Necklaces": [
        "https://images.unsplash.com/photo-1599643478518-a784e5dc4c8f?w=600&auto=format&fit=crop&q=80"
    ],
    "Bracelets": [
        "https://images.unsplash.com/photo-1611591475874-98c4749cb73b?w=600&auto=format&fit=crop&q=80"
    ],
    "Watches": [
        "https://images.unsplash.com/photo-1524592094714-0f0654e20314?w=600&auto=format&fit=crop&q=80",
        "https://images.unsplash.com/photo-1522335789203-aabd1fc54bc9?w=600&auto=format&fit=crop&q=80"
    ],
    "Dupattas": [
        "https://images.unsplash.com/photo-1609357605129-26f69add5d6e?w=600&auto=format&fit=crop&q=80"
    ],
    "Scarves": [
        "https://images.unsplash.com/photo-1601924994987-69e26d50dc26?w=600&auto=format&fit=crop&q=80"
    ],

    # Male Traditional
    "Sherwanis": [
        "https://images.unsplash.com/photo-1610030469983-98e550d6193c?w=600&auto=format&fit=crop&q=80",
        "https://images.unsplash.com/photo-1507679799987-c73779587ccf?w=600&auto=format&fit=crop&q=80"
    ],
    "Kurta pyjama sets": [
        "https://images.unsplash.com/photo-1609357605129-26f69add5d6e?w=600&auto=format&fit=crop&q=80"
    ],
    "Pathani suits": [
        "https://images.unsplash.com/photo-1609357605129-26f69add5d6e?w=600&auto=format&fit=crop&q=80"
    ],
    "Nehru jackets": [
        "https://images.unsplash.com/photo-1507679799987-c73779587ccf?w=600&auto=format&fit=crop&q=80"
    ],
    "Indo-western suits": [
        "https://images.unsplash.com/photo-1507679799987-c73779587ccf?w=600&auto=format&fit=crop&q=80"
    ],
    "Traditional waistcoats": [
        "https://images.unsplash.com/photo-1507679799987-c73779587ccf?w=600&auto=format&fit=crop&q=80"
    ],
    "Ethnic sets": [
        "https://images.unsplash.com/photo-1609357605129-26f69add5d6e?w=600&auto=format&fit=crop&q=80"
    ],
    # Male Western
    "Formal shirts": [
        "https://images.unsplash.com/photo-1596755094514-f87e34085b2c?w=600&auto=format&fit=crop&q=80",
        "https://images.unsplash.com/photo-1602810318383-e386cc2a3ccf?w=600&auto=format&fit=crop&q=80"
    ],
    "Casual shirts": [
        "https://images.unsplash.com/photo-1602810318383-e386cc2a3ccf?w=600&auto=format&fit=crop&q=80",
        "https://images.unsplash.com/photo-1596755094514-f87e34085b2c?w=600&auto=format&fit=crop&q=80"
    ],
    "T-shirts": [
        "https://images.unsplash.com/photo-1521572267360-ee0c2909d518?w=600&auto=format&fit=crop&q=80",
        "https://images.unsplash.com/photo-1583743814966-8936f5b7be1a?w=600&auto=format&fit=crop&q=80"
    ],
    "Polo T-shirts": [
        "https://images.unsplash.com/photo-1625910513413-562725e22709?w=600&auto=format&fit=crop&q=80"
    ],
    "Formal trousers": [
        "https://images.unsplash.com/photo-1594633312681-425c7b97ccd1?w=600&auto=format&fit=crop&q=80"
    ],
    "Chinos": [
        "https://images.unsplash.com/photo-1624378439575-d8705ad7ae80?w=600&auto=format&fit=crop&q=80"
    ],
    "Suits": [
        "https://images.unsplash.com/photo-1507679799987-c73779587ccf?w=600&auto=format&fit=crop&q=80"
    ],
    "Jackets": [
        "https://images.unsplash.com/photo-1551028719-00167b16eac5?w=600&auto=format&fit=crop&q=80"
    ],
    "Hoodies": [
        "https://images.unsplash.com/photo-1556905055-8f358a7a47b2?w=600&auto=format&fit=crop&q=80"
    ],
    # Male Footwear
    "Formal shoes": [
        "https://images.unsplash.com/photo-1614252235316-8c857d38b5f4?w=600&auto=format&fit=crop&q=80"
    ],
    "Loafers": [
        "https://images.unsplash.com/photo-1533867617858-e7b97e060509?w=600&auto=format&fit=crop&q=80"
    ],
    # Male Accessories
    "Belts": [
        "https://images.unsplash.com/photo-1624222247344-550fb60583dc?w=600&auto=format&fit=crop&q=80"
    ],
    "Wallets": [
        "https://images.unsplash.com/photo-1627123424574-724758594e93?w=600&auto=format&fit=crop&q=80"
    ],
    "Ties": [
        "https://images.unsplash.com/photo-1589756823695-278bc923f962?w=600&auto=format&fit=crop&q=80"
    ],
    "Pocket squares": [
        "https://images.unsplash.com/photo-1589756823695-278bc923f962?w=600&auto=format&fit=crop&q=80"
    ],
    "Sunglasses": [
        "https://images.unsplash.com/photo-1511499767150-a48a237f0083?w=600&auto=format&fit=crop&q=80"
    ],
    "Caps": [
        "https://images.unsplash.com/photo-1588850561407-ed78c282e89b?w=600&auto=format&fit=crop&q=80"
    ],
    "Backpacks": [
        "https://images.unsplash.com/photo-1553062407-98eeb64c6a62?w=600&auto=format&fit=crop&q=80"
    ]
}

DEFAULT_IMAGE = "https://images.unsplash.com/photo-1521572267360-ee0c2909d518?w=600&auto=format&fit=crop&q=80"

BRANDS = [
    "FabIndia", "Manyavar", "Biba", "W for Woman", "Sabyasachi Heritage",
    "Zara", "H&M", "Raymond", "Louis Philippe", "Peter England",
    "Allen Solly", "Nike", "Adidas", "Puma", "Aldo", "Titan", "Fossil",
    "Levi's", "Marks & Spencer", "Raw Mango Inspired", "Anita Dongre Heritage", "Mango"
]

def get_image(subcat):
    imgs = IMAGE_MAP.get(subcat, [])
    if imgs:
        return random.choice(imgs)
    # Check partial match
    for k, v in IMAGE_MAP.items():
        if k.lower() in subcat.lower() or subcat.lower() in k.lower():
            return random.choice(v)
    return DEFAULT_IMAGE


def generate_structured_catalog():
    """Generates >= 1,050 well-distributed products across Male, Female, and Unisex."""
    products = []
    pid = 1

    # Define Category Specifications
    female_specs = [
        # Traditional (Complete outfits or sets)
        {"main": "Traditional", "cat": "Clothing", "sub": "Sarees", "type": "Complete Outfit", "occasions": ["Wedding", "Engagement", "Festival", "Religious Event", "Family Gathering"], "fabrics": ["Silk", "Georgette", "Chiffon", "Organza", "Crepe"], "fits": ["Straight Fit", "Regular Fit"], "sleeves": ["Sleeveless", "Half Sleeve", "Full Sleeve"], "lengths": ["Floor Length"], "styles": ["Traditional", "Ethnic", "Elegant", "Luxury"], "price_range": (3499, 14999)},
        {"main": "Traditional", "cat": "Clothing", "sub": "Designer sarees", "type": "Complete Outfit", "occasions": ["Engagement", "Wedding", "Party", "Photoshoot", "Formal Event"], "fabrics": ["Silk", "Satin", "Organza", "Velvet"], "fits": ["Tailored Fit", "Regular Fit"], "sleeves": ["Sleeveless", "Full Sleeve"], "lengths": ["Floor Length"], "styles": ["Elegant", "Luxury", "Traditional", "Trendy"], "price_range": (4999, 18999)},
        {"main": "Traditional", "cat": "Clothing", "sub": "Lehengas", "type": "Complete Outfit", "occasions": ["Wedding", "Engagement", "Festival", "Family Gathering"], "fabrics": ["Silk", "Velvet", "Georgette", "Crepe"], "fits": ["Tailored Fit", "Regular Fit"], "sleeves": ["Half Sleeve", "Full Sleeve", "Sleeveless"], "lengths": ["Floor Length"], "styles": ["Traditional", "Ethnic", "Luxury", "Elegant"], "price_range": (5999, 19999)},
        {"main": "Traditional", "cat": "Clothing", "sub": "Anarkali suits", "type": "Complete Outfit", "occasions": ["Engagement", "Festival", "Religious Event", "Wedding", "Family Gathering"], "fabrics": ["Georgette", "Silk", "Chiffon", "Cotton"], "fits": ["Regular Fit", "Relaxed Fit"], "sleeves": ["Full Sleeve", "Three-Quarter Sleeve"], "lengths": ["Floor Length", "Ankle Length"], "styles": ["Traditional", "Ethnic", "Elegant"], "price_range": (2999, 8999)},
        {"main": "Traditional", "cat": "Clothing", "sub": "Salwar suits", "type": "Complete Outfit", "occasions": ["Religious Event", "Family Gathering", "Festival", "College", "Office"], "fabrics": ["Cotton", "Silk", "Khadi", "Rayon"], "fits": ["Regular Fit", "Straight Fit"], "sleeves": ["Three-Quarter Sleeve", "Full Sleeve"], "lengths": ["Ankle Length", "Standard"], "styles": ["Traditional", "Ethnic", "Classic"], "price_range": (1499, 4999)},
        {"main": "Traditional", "cat": "Clothing", "sub": "Sharara sets", "type": "Complete Outfit", "occasions": ["Engagement", "Wedding", "Festival", "Party"], "fabrics": ["Georgette", "Silk", "Crepe"], "fits": ["Relaxed Fit", "Straight Fit"], "sleeves": ["Three-Quarter Sleeve", "Full Sleeve"], "lengths": ["Floor Length"], "styles": ["Ethnic", "Traditional", "Trendy"], "price_range": (3499, 9999)},
        {"main": "Traditional", "cat": "Clothing", "sub": "Palazzo sets", "type": "Complete Outfit", "occasions": ["Brunch", "Casual Outing", "Family Gathering", "Office"], "fabrics": ["Cotton", "Rayon", "Linen", "Modal"], "fits": ["Relaxed Fit", "Loose Fit"], "sleeves": ["Half Sleeve", "Three-Quarter Sleeve"], "lengths": ["Ankle Length"], "styles": ["Casual", "Ethnic", "Minimal"], "price_range": (1299, 3999)},
        {"main": "Traditional", "cat": "Clothing", "sub": "Kurtis", "type": "Topwear", "occasions": ["College", "University", "Office", "Casual Outing", "Shopping"], "fabrics": ["Cotton", "Rayon", "Linen", "Khadi"], "fits": ["Regular Fit", "Straight Fit"], "sleeves": ["Three-Quarter Sleeve", "Half Sleeve"], "lengths": ["Standard", "Long"], "styles": ["Ethnic", "Casual", "Minimal"], "price_range": (699, 2199)},
        {"main": "Traditional", "cat": "Clothing", "sub": "Ethnic gowns", "type": "Complete Outfit", "occasions": ["Engagement", "Party", "Dinner", "Photoshoot"], "fabrics": ["Silk", "Georgette", "Satin"], "fits": ["Tailored Fit", "Regular Fit"], "sleeves": ["Full Sleeve", "Sleeveless"], "lengths": ["Floor Length"], "styles": ["Elegant", "Luxury", "Traditional"], "price_range": (3999, 12999)},
        {"main": "Traditional", "cat": "Clothing", "sub": "Indo-western outfits", "type": "Complete Outfit", "occasions": ["Engagement", "Party", "Cocktail", "Dinner", "Concert"], "fabrics": ["Silk", "Crepe", "Satin"], "fits": ["Tailored Fit", "Straight Fit"], "sleeves": ["Full Sleeve", "Sleeveless"], "lengths": ["Floor Length", "Ankle Length"], "styles": ["Trendy", "Elegant", "Luxury"], "price_range": (3999, 11999)},

        # Western (Female)
        {"main": "Western", "cat": "Clothing", "sub": "Dresses", "type": "Complete Outfit", "occasions": ["Date", "Dinner", "Party", "Brunch", "Birthday", "Vacation"], "fabrics": ["Cotton", "Linen", "Silk", "Satin", "Rayon"], "fits": ["Slim Fit", "Regular Fit", "Bodycon Fit", "Relaxed Fit"], "sleeves": ["Sleeveless", "Full Sleeve", "Half Sleeve"], "lengths": ["Short", "Standard", "Maxi"], "styles": ["Elegant", "Casual", "Minimal", "Trendy", "Y2K", "Bohemian"], "price_range": (1499, 5999)},
        {"main": "Western", "cat": "Clothing", "sub": "Tops", "type": "Topwear", "occasions": ["College", "Casual Outing", "Shopping", "Date", "Brunch"], "fabrics": ["Cotton", "Linen", "Rayon", "Knit", "Jersey"], "fits": ["Slim Fit", "Regular Fit", "Relaxed Fit", "Oversized"], "sleeves": ["Sleeveless", "Half Sleeve", "Full Sleeve"], "lengths": ["Cropped", "Standard"], "styles": ["Casual", "Streetwear", "Minimal", "Trendy", "Y2K"], "price_range": (599, 1999)},
        {"main": "Western", "cat": "Clothing", "sub": "Shirts", "type": "Topwear", "occasions": ["Office", "Business Meeting", "Interview", "Formal Event", "Semi-Formal Event"], "fabrics": ["Cotton", "Linen", "Silk", "Modal"], "fits": ["Tailored Fit", "Regular Fit", "Oversized"], "sleeves": ["Full Sleeve", "Three-Quarter Sleeve"], "lengths": ["Standard"], "styles": ["Formal", "Smart Casual", "Minimal", "Classic"], "price_range": (999, 2999)},
        {"main": "Western", "cat": "Clothing", "sub": "Jeans", "type": "Bottomwear", "occasions": ["College", "University", "Casual Outing", "Shopping", "Concert", "Travel"], "fabrics": ["Denim", "Cotton"], "fits": ["Straight Fit", "Relaxed Fit", "Oversized", "Slim Fit"], "sleeves": ["N/A"], "lengths": ["Ankle Length", "Standard"], "styles": ["Casual", "Streetwear", "Vintage", "Classic"], "price_range": (1299, 3999)},
        {"main": "Western", "cat": "Clothing", "sub": "Trousers", "type": "Bottomwear", "occasions": ["Office", "Business Meeting", "Interview", "Formal Event", "Dinner"], "fabrics": ["Wool", "Cotton", "Linen", "Crepe"], "fits": ["Tailored Fit", "Straight Fit", "Slim Fit"], "sleeves": ["N/A"], "lengths": ["Ankle Length", "Standard"], "styles": ["Formal", "Smart Casual", "Minimal", "Elegant"], "price_range": (1499, 4299)},
        {"main": "Western", "cat": "Clothing", "sub": "Skirts", "type": "Bottomwear", "occasions": ["Date", "Brunch", "Party", "Vacation", "Casual Outing"], "fabrics": ["Cotton", "Denim", "Satin", "Linen"], "fits": ["Straight Fit", "Relaxed Fit", "Slim Fit"], "sleeves": ["N/A"], "lengths": ["Short", "Standard", "Maxi"], "styles": ["Casual", "Preppy", "Elegant", "Vintage"], "price_range": (999, 2799)},
        {"main": "Western", "cat": "Clothing", "sub": "Jumpsuits", "type": "Complete Outfit", "occasions": ["Party", "Dinner", "Brunch", "Casual Outing", "Travel"], "fabrics": ["Rayon", "Cotton", "Linen", "Crepe"], "fits": ["Tailored Fit", "Relaxed Fit"], "sleeves": ["Sleeveless", "Full Sleeve"], "lengths": ["Ankle Length", "Standard"], "styles": ["Smart Casual", "Trendy", "Elegant"], "price_range": (1899, 4999)},
        {"main": "Western", "cat": "Clothing", "sub": "Blazers", "type": "Topwear", "occasions": ["Office", "Business Meeting", "Interview", "Formal Event", "Semi-Formal Event"], "fabrics": ["Wool", "Linen", "Cotton", "Velvet"], "fits": ["Tailored Fit", "Slim Fit", "Oversized"], "sleeves": ["Full Sleeve"], "lengths": ["Standard", "Long"], "styles": ["Formal", "Smart Casual", "Preppy", "Luxury"], "price_range": (2999, 8999)},
        {"main": "Western", "cat": "Clothing", "sub": "Co-ord sets", "type": "Complete Outfit", "occasions": ["Vacation", "Brunch", "Party", "Travel", "Photoshoot"], "fabrics": ["Linen", "Cotton", "Satin", "Knit"], "fits": ["Relaxed Fit", "Regular Fit"], "sleeves": ["Half Sleeve", "Full Sleeve"], "lengths": ["Standard", "Short"], "styles": ["Trendy", "Casual", "Minimal", "Luxury"], "price_range": (2199, 5999)},
        {"main": "Western", "cat": "Clothing", "sub": "Casual wear", "type": "Topwear", "occasions": ["Casual Outing", "College", "Shopping", "Beach", "Travel"], "fabrics": ["Cotton", "Modal", "Jersey"], "fits": ["Relaxed Fit", "Oversized"], "sleeves": ["Half Sleeve", "Full Sleeve"], "lengths": ["Standard"], "styles": ["Casual", "Streetwear", "Athleisure"], "price_range": (699, 1899)},

        # Female Footwear
        {"main": "Footwear", "cat": "Footwear", "sub": "Heels", "type": "Footwear", "occasions": ["Engagement", "Wedding", "Party", "Dinner", "Formal Event"], "fabrics": ["Leather", "Satin", "Velvet"], "fits": ["Tailored Fit"], "sleeves": ["N/A"], "lengths": ["N/A"], "styles": ["Elegant", "Luxury", "Traditional", "Formal"], "price_range": (1899, 6999)},
        {"main": "Footwear", "cat": "Footwear", "sub": "Flats", "type": "Footwear", "occasions": ["College", "Casual Outing", "Office", "Shopping", "Travel"], "fabrics": ["Leather", "Synthetic"], "fits": ["Regular Fit"], "sleeves": ["N/A"], "lengths": ["N/A"], "styles": ["Casual", "Minimal", "Classic"], "price_range": (899, 2499)},
        {"main": "Footwear", "cat": "Footwear", "sub": "Sandals", "type": "Footwear", "occasions": ["Brunch", "Beach", "Vacation", "Casual Outing"], "fabrics": ["Leather", "Synthetic"], "fits": ["Regular Fit"], "sleeves": ["N/A"], "lengths": ["N/A"], "styles": ["Bohemian", "Casual", "Minimal"], "price_range": (799, 2199)},
        {"main": "Footwear", "cat": "Footwear", "sub": "Ethnic footwear", "type": "Footwear", "occasions": ["Engagement", "Wedding", "Festival", "Religious Event", "Family Gathering"], "fabrics": ["Leather", "Silk", "Velvet"], "fits": ["Regular Fit"], "sleeves": ["N/A"], "lengths": ["N/A"], "styles": ["Traditional", "Ethnic", "Luxury"], "price_range": (1299, 4499)},
        {"main": "Footwear", "cat": "Footwear", "sub": "Sneakers", "type": "Footwear", "occasions": ["College", "University", "Casual Outing", "Travel", "Gym", "Sports"], "fabrics": ["Leather", "Canvas", "Jersey"], "fits": ["Regular Fit"], "sleeves": ["N/A"], "lengths": ["N/A"], "styles": ["Casual", "Streetwear", "Sporty", "Athleisure"], "price_range": (1899, 5999)},
        {"main": "Footwear", "cat": "Footwear", "sub": "Boots", "type": "Footwear", "occasions": ["Concert", "Dinner", "Travel", "Photoshoot", "Party"], "fabrics": ["Leather", "Suede"], "fits": ["Regular Fit"], "sleeves": ["N/A"], "lengths": ["N/A"], "styles": ["Streetwear", "Trendy", "Vintage", "Classic"], "price_range": (2499, 6999)},

        # Female Accessories
        {"main": "Accessories", "cat": "Accessories", "sub": "Handbags", "type": "Accessory", "occasions": ["Office", "Shopping", "Brunch", "Travel", "Formal Event"], "fabrics": ["Leather", "Canvas"], "fits": ["N/A"], "sleeves": ["N/A"], "lengths": ["N/A"], "styles": ["Elegant", "Formal", "Classic", "Minimal"], "price_range": (1499, 4999)},
        {"main": "Accessories", "cat": "Accessories", "sub": "Clutches", "type": "Accessory", "occasions": ["Engagement", "Wedding", "Party", "Dinner", "Formal Event"], "fabrics": ["Silk", "Satin", "Velvet", "Leather"], "fits": ["N/A"], "sleeves": ["N/A"], "lengths": ["N/A"], "styles": ["Luxury", "Elegant", "Traditional"], "price_range": (999, 3999)},
        {"main": "Accessories", "cat": "Accessories", "sub": "Earrings", "type": "Accessory", "occasions": ["Engagement", "Wedding", "Festival", "Party", "Date"], "fabrics": ["Metal", "Gold-Plated"], "fits": ["N/A"], "sleeves": ["N/A"], "lengths": ["N/A"], "styles": ["Traditional", "Ethnic", "Luxury", "Minimal"], "price_range": (499, 2999)},
        {"main": "Accessories", "cat": "Accessories", "sub": "Necklaces", "type": "Accessory", "occasions": ["Engagement", "Wedding", "Festival", "Formal Event", "Party"], "fabrics": ["Metal", "Gold-Plated"], "fits": ["N/A"], "sleeves": ["N/A"], "lengths": ["N/A"], "styles": ["Traditional", "Ethnic", "Luxury", "Elegant"], "price_range": (799, 4999)},
        {"main": "Accessories", "cat": "Accessories", "sub": "Watches", "type": "Accessory", "occasions": ["Office", "Business Meeting", "College", "Formal Event", "Casual Outing"], "fabrics": ["Leather", "Stainless Steel"], "fits": ["N/A"], "sleeves": ["N/A"], "lengths": ["N/A"], "styles": ["Classic", "Minimal", "Formal", "Luxury"], "price_range": (1999, 7999)},
        {"main": "Accessories", "cat": "Accessories", "sub": "Dupattas", "type": "Accessory", "occasions": ["Religious Event", "Festival", "Family Gathering", "Wedding"], "fabrics": ["Silk", "Chiffon", "Organza"], "fits": ["N/A"], "sleeves": ["N/A"], "lengths": ["N/A"], "styles": ["Traditional", "Ethnic"], "price_range": (599, 1999)}
    ]

    male_specs = [
        # Traditional (Male)
        {"main": "Traditional", "cat": "Clothing", "sub": "Sherwanis", "type": "Complete Outfit", "occasions": ["Engagement", "Wedding", "Festival", "Photoshoot"], "fabrics": ["Silk", "Velvet", "Georgette", "Brocade"], "fits": ["Tailored Fit", "Regular Fit"], "sleeves": ["Full Sleeve"], "lengths": ["Long", "Floor Length"], "styles": ["Traditional", "Ethnic", "Luxury", "Elegant"], "price_range": (5999, 19999)},
        {"main": "Traditional", "cat": "Clothing", "sub": "Kurta pyjama sets", "type": "Complete Outfit", "occasions": ["Festival", "Religious Event", "Family Gathering", "Wedding", "Engagement"], "fabrics": ["Cotton", "Silk", "Linen", "Khadi"], "fits": ["Regular Fit", "Relaxed Fit"], "sleeves": ["Full Sleeve"], "lengths": ["Long", "Ankle Length"], "styles": ["Traditional", "Ethnic", "Classic"], "price_range": (1899, 6999)},
        {"main": "Traditional", "cat": "Clothing", "sub": "Pathani suits", "type": "Complete Outfit", "occasions": ["Festival", "Family Gathering", "Religious Event", "Casual Outing"], "fabrics": ["Cotton", "Linen"], "fits": ["Relaxed Fit", "Regular Fit"], "sleeves": ["Full Sleeve"], "lengths": ["Long"], "styles": ["Traditional", "Ethnic", "Classic"], "price_range": (1999, 4999)},
        {"main": "Traditional", "cat": "Clothing", "sub": "Nehru jackets", "type": "Topwear", "occasions": ["Engagement", "Wedding", "Festival", "Semi-Formal Event", "Family Gathering"], "fabrics": ["Silk", "Linen", "Wool", "Khadi"], "fits": ["Tailored Fit", "Slim Fit"], "sleeves": ["Sleeveless"], "lengths": ["Standard"], "styles": ["Traditional", "Ethnic", "Elegant", "Smart Casual"], "price_range": (1999, 5999)},
        {"main": "Traditional", "cat": "Clothing", "sub": "Indo-western outfits", "type": "Complete Outfit", "occasions": ["Engagement", "Party", "Wedding", "Cocktail", "Dinner"], "fabrics": ["Silk", "Wool", "Velvet"], "fits": ["Tailored Fit"], "sleeves": ["Full Sleeve"], "lengths": ["Long"], "styles": ["Luxury", "Elegant", "Trendy", "Traditional"], "price_range": (4999, 15999)},
        {"main": "Traditional", "cat": "Clothing", "sub": "Traditional waistcoats", "type": "Topwear", "occasions": ["Festival", "Family Gathering", "Semi-Formal Event"], "fabrics": ["Silk", "Khadi", "Linen"], "fits": ["Tailored Fit"], "sleeves": ["Sleeveless"], "lengths": ["Standard"], "styles": ["Traditional", "Ethnic", "Classic"], "price_range": (1499, 3999)},
        {"main": "Traditional", "cat": "Clothing", "sub": "Ethnic sets", "type": "Complete Outfit", "occasions": ["Festival", "Religious Event", "Brunch", "Family Gathering"], "fabrics": ["Cotton", "Linen", "Silk"], "fits": ["Regular Fit", "Relaxed Fit"], "sleeves": ["Full Sleeve"], "lengths": ["Standard"], "styles": ["Traditional", "Ethnic", "Minimal"], "price_range": (1799, 5499)},

        # Western (Male)
        {"main": "Western", "cat": "Clothing", "sub": "Formal shirts", "type": "Topwear", "occasions": ["Office", "Business Meeting", "Interview", "Formal Event", "Dinner"], "fabrics": ["Cotton", "Linen", "Modal"], "fits": ["Slim Fit", "Regular Fit", "Tailored Fit"], "sleeves": ["Full Sleeve"], "lengths": ["Standard"], "styles": ["Formal", "Classic", "Minimal", "Smart Casual"], "price_range": (1199, 3499)},
        {"main": "Western", "cat": "Clothing", "sub": "Casual shirts", "type": "Topwear", "occasions": ["College", "University", "Brunch", "Date", "Casual Outing", "Vacation"], "fabrics": ["Cotton", "Linen", "Denim"], "fits": ["Regular Fit", "Relaxed Fit", "Oversized"], "sleeves": ["Half Sleeve", "Full Sleeve"], "lengths": ["Standard"], "styles": ["Casual", "Smart Casual", "Streetwear", "Minimal"], "price_range": (899, 2499)},
        {"main": "Western", "cat": "Clothing", "sub": "T-shirts", "type": "Topwear", "occasions": ["College", "Casual Outing", "Shopping", "Concert", "Travel", "Beach"], "fabrics": ["Cotton", "Jersey", "Modal"], "fits": ["Regular Fit", "Oversized", "Relaxed Fit", "Slim Fit"], "sleeves": ["Half Sleeve", "Full Sleeve"], "lengths": ["Standard"], "styles": ["Casual", "Streetwear", "Minimal", "Trendy", "Y2K"], "price_range": (499, 1499)},
        {"main": "Western", "cat": "Clothing", "sub": "Polo T-shirts", "type": "Topwear", "occasions": ["Brunch", "Casual Outing", "Sports", "Vacation", "Semi-Formal Event"], "fabrics": ["Cotton", "Knit"], "fits": ["Regular Fit", "Slim Fit"], "sleeves": ["Half Sleeve"], "lengths": ["Standard"], "styles": ["Preppy", "Casual", "Smart Casual", "Classic"], "price_range": (799, 2199)},
        {"main": "Western", "cat": "Clothing", "sub": "Jeans", "type": "Bottomwear", "occasions": ["College", "Casual Outing", "Concert", "Shopping", "Travel"], "fabrics": ["Denim", "Cotton"], "fits": ["Straight Fit", "Slim Fit", "Relaxed Fit", "Oversized"], "sleeves": ["N/A"], "lengths": ["Standard", "Ankle Length"], "styles": ["Casual", "Streetwear", "Vintage", "Classic"], "price_range": (1299, 3999)},
        {"main": "Western", "cat": "Clothing", "sub": "Formal trousers", "type": "Bottomwear", "occasions": ["Office", "Business Meeting", "Interview", "Formal Event"], "fabrics": ["Wool", "Cotton", "Linen"], "fits": ["Tailored Fit", "Slim Fit", "Straight Fit"], "sleeves": ["N/A"], "lengths": ["Standard"], "styles": ["Formal", "Classic", "Minimal"], "price_range": (1499, 3999)},
        {"main": "Western", "cat": "Clothing", "sub": "Chinos", "type": "Bottomwear", "occasions": ["Office", "Brunch", "Date", "Semi-Formal Event", "Casual Outing"], "fabrics": ["Cotton", "Linen"], "fits": ["Slim Fit", "Straight Fit", "Regular Fit"], "sleeves": ["N/A"], "lengths": ["Standard", "Ankle Length"], "styles": ["Smart Casual", "Preppy", "Minimal", "Casual"], "price_range": (1299, 2999)},
        {"main": "Western", "cat": "Clothing", "sub": "Blazers", "type": "Topwear", "occasions": ["Office", "Business Meeting", "Interview", "Formal Event", "Semi-Formal Event", "Dinner"], "fabrics": ["Wool", "Linen", "Cotton"], "fits": ["Tailored Fit", "Slim Fit"], "sleeves": ["Full Sleeve"], "lengths": ["Standard"], "styles": ["Formal", "Smart Casual", "Classic", "Luxury"], "price_range": (3499, 9999)},
        {"main": "Western", "cat": "Clothing", "sub": "Suits", "type": "Complete Outfit", "occasions": ["Business Meeting", "Formal Event", "Interview", "Engagement", "Wedding"], "fabrics": ["Wool", "Linen"], "fits": ["Tailored Fit", "Slim Fit"], "sleeves": ["Full Sleeve"], "lengths": ["Standard"], "styles": ["Formal", "Classic", "Luxury"], "price_range": (5999, 18999)},
        {"main": "Western", "cat": "Clothing", "sub": "Jackets", "type": "Topwear", "occasions": ["Travel", "Concert", "Casual Outing", "Vacation"], "fabrics": ["Leather", "Denim", "Cotton", "Polyester"], "fits": ["Relaxed Fit", "Regular Fit", "Oversized"], "sleeves": ["Full Sleeve"], "lengths": ["Standard"], "styles": ["Streetwear", "Casual", "Vintage"], "price_range": (2199, 6999)},
        {"main": "Western", "cat": "Clothing", "sub": "Hoodies", "type": "Topwear", "occasions": ["College", "Casual Outing", "Gym", "Travel"], "fabrics": ["Cotton", "Fleece", "Jersey"], "fits": ["Oversized", "Relaxed Fit"], "sleeves": ["Full Sleeve"], "lengths": ["Standard"], "styles": ["Streetwear", "Casual", "Athleisure"], "price_range": (1199, 2999)},
        {"main": "Western", "cat": "Clothing", "sub": "Co-ord sets", "type": "Complete Outfit", "occasions": ["Brunch", "Vacation", "Beach", "Casual Outing", "Travel"], "fabrics": ["Linen", "Cotton"], "fits": ["Relaxed Fit"], "sleeves": ["Half Sleeve"], "lengths": ["Short", "Standard"], "styles": ["Casual", "Trendy", "Minimal"], "price_range": (1999, 4999)},

        # Male Footwear
        {"main": "Footwear", "cat": "Footwear", "sub": "Formal shoes", "type": "Footwear", "occasions": ["Office", "Business Meeting", "Interview", "Formal Event", "Dinner"], "fabrics": ["Leather"], "fits": ["Tailored Fit"], "sleeves": ["N/A"], "lengths": ["N/A"], "styles": ["Formal", "Classic", "Luxury"], "price_range": (1999, 6499)},
        {"main": "Footwear", "cat": "Footwear", "sub": "Loafers", "type": "Footwear", "occasions": ["Brunch", "Office", "Semi-Formal Event", "Date", "Casual Outing"], "fabrics": ["Leather", "Suede"], "fits": ["Regular Fit"], "sleeves": ["N/A"], "lengths": ["N/A"], "styles": ["Smart Casual", "Preppy", "Classic", "Minimal"], "price_range": (1699, 4999)},
        {"main": "Footwear", "cat": "Footwear", "sub": "Sneakers", "type": "Footwear", "occasions": ["College", "Casual Outing", "Shopping", "Travel", "Gym", "Sports"], "fabrics": ["Leather", "Canvas"], "fits": ["Regular Fit"], "sleeves": ["N/A"], "lengths": ["N/A"], "styles": ["Casual", "Streetwear", "Athleisure", "Sporty"], "price_range": (1999, 6999)},
        {"main": "Footwear", "cat": "Footwear", "sub": "Sandals", "type": "Footwear", "occasions": ["Beach", "Casual Outing", "Vacation"], "fabrics": ["Leather", "Synthetic"], "fits": ["Regular Fit"], "sleeves": ["N/A"], "lengths": ["N/A"], "styles": ["Casual", "Bohemian"], "price_range": (799, 1999)},
        {"main": "Footwear", "cat": "Footwear", "sub": "Ethnic footwear", "type": "Footwear", "occasions": ["Engagement", "Wedding", "Festival", "Religious Event", "Family Gathering"], "fabrics": ["Leather", "Velvet", "Silk"], "fits": ["Regular Fit"], "sleeves": ["N/A"], "lengths": ["N/A"], "styles": ["Traditional", "Ethnic", "Luxury"], "price_range": (1499, 4499)},
        {"main": "Footwear", "cat": "Footwear", "sub": "Boots", "type": "Footwear", "occasions": ["Concert", "Travel", "Winter", "Casual Outing"], "fabrics": ["Leather", "Suede"], "fits": ["Regular Fit"], "sleeves": ["N/A"], "lengths": ["N/A"], "styles": ["Streetwear", "Vintage", "Classic"], "price_range": (2499, 6999)},

        # Male Accessories
        {"main": "Accessories", "cat": "Accessories", "sub": "Watches", "type": "Accessory", "occasions": ["Office", "Business Meeting", "Engagement", "Formal Event", "College"], "fabrics": ["Leather", "Stainless Steel"], "fits": ["N/A"], "sleeves": ["N/A"], "lengths": ["N/A"], "styles": ["Classic", "Minimal", "Formal", "Luxury"], "price_range": (1999, 8999)},
        {"main": "Accessories", "cat": "Accessories", "sub": "Belts", "type": "Accessory", "occasions": ["Office", "Business Meeting", "Formal Event", "Casual Outing"], "fabrics": ["Leather"], "fits": ["N/A"], "sleeves": ["N/A"], "lengths": ["N/A"], "styles": ["Formal", "Classic"], "price_range": (699, 2199)},
        {"main": "Accessories", "cat": "Accessories", "sub": "Wallets", "type": "Accessory", "occasions": ["Office", "Casual Outing", "Travel"], "fabrics": ["Leather"], "fits": ["N/A"], "sleeves": ["N/A"], "lengths": ["N/A"], "styles": ["Minimal", "Classic"], "price_range": (699, 1999)},
        {"main": "Accessories", "cat": "Accessories", "sub": "Ties", "type": "Accessory", "occasions": ["Office", "Business Meeting", "Interview", "Formal Event"], "fabrics": ["Silk", "Microfiber"], "fits": ["N/A"], "sleeves": ["N/A"], "lengths": ["N/A"], "styles": ["Formal", "Classic"], "price_range": (499, 1499)},
        {"main": "Accessories", "cat": "Accessories", "sub": "Pocket squares", "type": "Accessory", "occasions": ["Engagement", "Wedding", "Formal Event", "Business Meeting"], "fabrics": ["Silk", "Linen"], "fits": ["N/A"], "sleeves": ["N/A"], "lengths": ["N/A"], "styles": ["Luxury", "Elegant", "Formal"], "price_range": (399, 1199)},
        {"main": "Accessories", "cat": "Accessories", "sub": "Sunglasses", "type": "Accessory", "occasions": ["Brunch", "Beach", "Travel", "Vacation", "Casual Outing"], "fabrics": ["Acetate", "Metal"], "fits": ["N/A"], "sleeves": ["N/A"], "lengths": ["N/A"], "styles": ["Trendy", "Classic", "Minimal"], "price_range": (999, 3999)},
        {"main": "Accessories", "cat": "Accessories", "sub": "Caps", "type": "Accessory", "occasions": ["College", "Sports", "Casual Outing", "Gym"], "fabrics": ["Cotton"], "fits": ["N/A"], "sleeves": ["N/A"], "lengths": ["N/A"], "styles": ["Streetwear", "Sporty", "Casual"], "price_range": (499, 1299)}
    ]

    unisex_specs = [
        {"main": "Western", "cat": "Clothing", "sub": "Basic T-shirts", "type": "Topwear", "occasions": ["College", "Casual Outing", "Shopping", "Travel", "Gym"], "fabrics": ["Cotton", "Modal"], "fits": ["Regular Fit", "Relaxed Fit", "Oversized"], "sleeves": ["Half Sleeve"], "lengths": ["Standard"], "styles": ["Casual", "Minimal", "Streetwear"], "price_range": (499, 1299)},
        {"main": "Western", "cat": "Clothing", "sub": "Hoodies", "type": "Topwear", "occasions": ["College", "Travel", "Casual Outing", "Concert"], "fabrics": ["Cotton", "Fleece"], "fits": ["Oversized", "Relaxed Fit"], "sleeves": ["Full Sleeve"], "lengths": ["Standard"], "styles": ["Streetwear", "Casual", "Athleisure"], "price_range": (1299, 3299)},
        {"main": "Western", "cat": "Clothing", "sub": "Sweatshirts", "type": "Topwear", "occasions": ["College", "Travel", "Casual Outing", "Shopping"], "fabrics": ["Cotton", "Knit"], "fits": ["Relaxed Fit", "Oversized"], "sleeves": ["Full Sleeve"], "lengths": ["Standard"], "styles": ["Casual", "Streetwear", "Minimal"], "price_range": (1199, 2999)},
        {"main": "Footwear", "cat": "Footwear", "sub": "Sneakers", "type": "Footwear", "occasions": ["College", "Casual Outing", "Travel", "Gym", "Shopping"], "fabrics": ["Leather", "Canvas"], "fits": ["Regular Fit"], "sleeves": ["N/A"], "lengths": ["N/A"], "styles": ["Streetwear", "Casual", "Minimal", "Athleisure"], "price_range": (1999, 6499)},
        {"main": "Western", "cat": "Clothing", "sub": "Casual jackets", "type": "Topwear", "occasions": ["Travel", "Concert", "Casual Outing"], "fabrics": ["Denim", "Cotton", "Polyester"], "fits": ["Relaxed Fit", "Oversized"], "sleeves": ["Full Sleeve"], "lengths": ["Standard"], "styles": ["Casual", "Streetwear"], "price_range": (1999, 4999)},
        {"main": "Accessories", "cat": "Accessories", "sub": "Backpacks", "type": "Accessory", "occasions": ["College", "Travel", "Shopping", "Office", "Vacation"], "fabrics": ["Canvas", "Polyester", "Leather"], "fits": ["N/A"], "sleeves": ["N/A"], "lengths": ["N/A"], "styles": ["Minimal", "Casual", "Streetwear"], "price_range": (999, 3499)},
        {"main": "Accessories", "cat": "Accessories", "sub": "Sunglasses", "type": "Accessory", "occasions": ["Vacation", "Beach", "Travel", "Brunch"], "fabrics": ["Acetate", "Metal"], "fits": ["N/A"], "sleeves": ["N/A"], "lengths": ["N/A"], "styles": ["Classic", "Minimal", "Trendy"], "price_range": (999, 3499)}
    ]

    all_colors_keys = list(COLOR_FAMILIES.keys())
    
    # Generate Female products (~550 products)
    for spec in female_specs:
        # Generate 16-20 variants per spec across different colors, occasions, fabrics, fits
        num_variants = 18 if spec["main"] in ["Traditional", "Western"] else 12
        for i in range(num_variants):
            color = random.choice(all_colors_keys)
            color_family = COLOR_FAMILIES[color]
            fabric = random.choice(spec["fabrics"])
            fit = random.choice(spec["fits"])
            sleeve = random.choice(spec["sleeves"])
            length = random.choice(spec["lengths"])
            style = random.choice(spec["styles"])
            brand = random.choice(BRANDS)
            primary_occ = spec["occasions"][i % len(spec["occasions"])]
            supp_occs = list(set([primary_occ] + random.sample(OCCASIONS, min(4, len(OCCASIONS)))))
            price = round(random.randint(spec["price_range"][0], spec["price_range"][1]) / 50) * 50 - 1  # e.g. 2999
            
            p_name = f"{brand} {color} {fit if fit != 'N/A' else ''} {fabric} {spec['sub']}".replace("  ", " ").strip()
            img = get_image(spec["sub"])
            
            # Formality
            formality = "Casual"
            if primary_occ in ["Engagement", "Wedding", "Festival"]:
                formality = "Festive/Traditional"
            elif primary_occ in ["Office", "Business Meeting", "Interview", "Formal Event"]:
                formality = "Formal"
            elif primary_occ in ["Dinner", "Semi-Formal Event", "Party"]:
                formality = "Semi-Formal"
            elif primary_occ in ["Brunch", "Date"]:
                formality = "Smart Casual"

            compat = "complete_outfit" if spec["type"] == "Complete Outfit" else ("top" if spec["type"] == "Topwear" else ("bottom" if spec["type"] == "Bottomwear" else ("footwear" if spec["cat"] == "Footwear" else "accessory")))

            prod = {
                "id": pid,
                "name": p_name,
                "gender": "Female",
                "main_category": spec["main"],
                "category": spec["cat"],
                "subcategory": spec["sub"],
                "occasion": primary_occ,
                "supported_occasions": ", ".join(supp_occs),
                "clothing_type": spec["type"],
                "style_archetype": style,
                "style": style,
                "color": color,
                "color_family": color_family,
                "fabric": fabric,
                "material": fabric,
                "pattern": random.choice(["Solid", "Printed", "Embroidered", "Zari Work", "Striped", "Floral", "Textured"]),
                "fit": fit,
                "sleeve_length": sleeve,
                "garment_length": length,
                "body_shape_compatibility": random.choice(BODY_SHAPES),
                "skin_tone_compatibility": random.choice(SKIN_TONES),
                "season": random.choice(["Summer", "Winter", "All-Season", "Spring", "Monsoon"]),
                "weather_suitability": random.choice(["Mild", "Hot", "Cold", "All-Weather"]),
                "price": float(price),
                "brand": brand,
                "rating": round(random.uniform(4.3, 4.9), 1),
                "availability": True,
                "image_url": img,
                "description": f"Exquisitely tailored {p_name} crafted from pure {fabric} with flattering {fit} silhouette. Perfect for {primary_occ} styling.",
                "formality_level": formality,
                "outfit_compatibility": compat
            }
            products.append(prod)
            pid += 1

    # Generate Male products (~450 products)
    for spec in male_specs:
        num_variants = 18 if spec["main"] in ["Traditional", "Western"] else 12
        for i in range(num_variants):
            color = random.choice(all_colors_keys)
            color_family = COLOR_FAMILIES[color]
            fabric = random.choice(spec["fabrics"])
            fit = random.choice(spec["fits"])
            sleeve = random.choice(spec["sleeves"])
            length = random.choice(spec["lengths"])
            style = random.choice(spec["styles"])
            brand = random.choice(BRANDS)
            primary_occ = spec["occasions"][i % len(spec["occasions"])]
            supp_occs = list(set([primary_occ] + random.sample(OCCASIONS, min(4, len(OCCASIONS)))))
            price = round(random.randint(spec["price_range"][0], spec["price_range"][1]) / 50) * 50 - 1
            
            p_name = f"{brand} {color} {fit if fit != 'N/A' else ''} {fabric} {spec['sub']}".replace("  ", " ").strip()
            img = get_image(spec["sub"])

            formality = "Casual"
            if primary_occ in ["Engagement", "Wedding", "Festival"]:
                formality = "Festive/Traditional"
            elif primary_occ in ["Office", "Business Meeting", "Interview", "Formal Event"]:
                formality = "Formal"
            elif primary_occ in ["Dinner", "Semi-Formal Event", "Party"]:
                formality = "Semi-Formal"
            elif primary_occ in ["Brunch", "Date"]:
                formality = "Smart Casual"

            compat = "complete_outfit" if spec["type"] == "Complete Outfit" else ("top" if spec["type"] == "Topwear" else ("bottom" if spec["type"] == "Bottomwear" else ("footwear" if spec["cat"] == "Footwear" else "accessory")))

            prod = {
                "id": pid,
                "name": p_name,
                "gender": "Male",
                "main_category": spec["main"],
                "category": spec["cat"],
                "subcategory": spec["sub"],
                "occasion": primary_occ,
                "supported_occasions": ", ".join(supp_occs),
                "clothing_type": spec["type"],
                "style_archetype": style,
                "style": style,
                "color": color,
                "color_family": color_family,
                "fabric": fabric,
                "material": fabric,
                "pattern": random.choice(["Solid", "Textured", "Checked", "Striped", "Embroidered"]),
                "fit": fit,
                "sleeve_length": sleeve,
                "garment_length": length,
                "body_shape_compatibility": random.choice(BODY_SHAPES),
                "skin_tone_compatibility": random.choice(SKIN_TONES),
                "season": random.choice(["Summer", "Winter", "All-Season", "Autumn"]),
                "weather_suitability": random.choice(["Mild", "Hot", "Cold", "All-Weather"]),
                "price": float(price),
                "brand": brand,
                "rating": round(random.uniform(4.3, 4.9), 1),
                "availability": True,
                "image_url": img,
                "description": f"Refined {p_name} crafted with superior {fabric} and tailored {fit}. Curated for distinguished {primary_occ} moments.",
                "formality_level": formality,
                "outfit_compatibility": compat
            }
            products.append(prod)
            pid += 1

    # Generate Unisex products (~120 products)
    for spec in unisex_specs:
        for i in range(16):
            color = random.choice(all_colors_keys)
            color_family = COLOR_FAMILIES[color]
            fabric = random.choice(spec["fabrics"])
            fit = random.choice(spec["fits"])
            sleeve = random.choice(spec["sleeves"])
            length = random.choice(spec["lengths"])
            style = random.choice(spec["styles"])
            brand = random.choice(["Nike", "Adidas", "Puma", "Zara", "H&M", "Levi's", "Fastrack"])
            primary_occ = spec["occasions"][i % len(spec["occasions"])]
            supp_occs = list(set([primary_occ] + random.sample(OCCASIONS, min(4, len(OCCASIONS)))))
            price = round(random.randint(spec["price_range"][0], spec["price_range"][1]) / 50) * 50 - 1
            
            p_name = f"{brand} Unisex {color} {fit if fit != 'N/A' else ''} {fabric} {spec['sub']}".replace("  ", " ").strip()
            img = get_image(spec["sub"])

            compat = "top" if spec["type"] == "Topwear" else ("footwear" if spec["cat"] == "Footwear" else "accessory")

            prod = {
                "id": pid,
                "name": p_name,
                "gender": "Unisex",
                "main_category": spec["main"],
                "category": spec["cat"],
                "subcategory": spec["sub"],
                "occasion": primary_occ,
                "supported_occasions": ", ".join(supp_occs),
                "clothing_type": spec["type"],
                "style_archetype": style,
                "style": style,
                "color": color,
                "color_family": color_family,
                "fabric": fabric,
                "material": fabric,
                "pattern": random.choice(["Solid", "Graphic", "Textured", "Striped"]),
                "fit": fit,
                "sleeve_length": sleeve,
                "garment_length": length,
                "body_shape_compatibility": "All",
                "skin_tone_compatibility": "All",
                "season": "All-Season",
                "weather_suitability": "All-Weather",
                "price": float(price),
                "brand": brand,
                "rating": round(random.uniform(4.4, 4.8), 1),
                "availability": True,
                "image_url": img,
                "description": f"Versatile unisex {p_name} offering relaxed comfort and clean contemporary aesthetics.",
                "formality_level": "Casual",
                "outfit_compatibility": compat
            }
            products.append(prod)
            pid += 1

    return products


if __name__ == "__main__":
    catalog = generate_structured_catalog()
    print(f"Generated {len(catalog)} total fashion products!")
    female_cnt = sum(1 for p in catalog if p["gender"] == "Female")
    male_cnt = sum(1 for p in catalog if p["gender"] == "Male")
    unisex_cnt = sum(1 for p in catalog if p["gender"] == "Unisex")
    print(f"Distribution: Female: {female_cnt}, Male: {male_cnt}, Unisex: {unisex_cnt}")

    out_path = os.path.join(os.path.dirname(__file__), "fashion_catalog.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(catalog, f, indent=2)
    print(f"Saved to {out_path}")

