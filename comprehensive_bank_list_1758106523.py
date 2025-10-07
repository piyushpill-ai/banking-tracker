#!/usr/bin/env python3
"""
Comprehensive Australian Banking Institution List
Generated from CDR Register API: 2025-09-17 20:55:23
Total Banks: 120
"""

# Format: (Bank Name, Brand ID, Products Endpoint, Base URI, Logo URI)
COMPREHENSIVE_BANK_LIST = [
    ("Alex.Bank", "alexbank", "https://public.cdr.alex.com.au/cds-au/v1/banking/products", "https://public.cdr.alex.com.au", "https://www.alex.bank/assets/alex-bank-logo.png"),
    ("AMP Bank GO", "amp-bank-go", "https://pub.cdr-sme.amp.com.au/cds-au/v1/banking/products", "https://pub.cdr-sme.amp.com.au/api", "https://www.amp.com.au/content/dam/bank-app/amp-bank-logo-open-banking.png"),
    ("MyState Bank", "mystate-bank", "https://public.cdr.mystate.com.au/cds-au/v1/banking/products", "https://public.cdr.mystate.com.au", "https://mystate.com.au/wp-content/uploads/MyState_Logo_s.png"),
    ("PayPal Australia", "paypal-australia", "https://api.paypal.com/v1/identity/cds-au/v1/banking/products", "https://api.paypal.com/v1/identity", "https://newsroom.au.paypal-corp.com/image/pp_h_rgb.jpg"),
    ("Wise", "wise", "https://au-cdrbanking-pub.wise.com/cds-au/v1/banking/products", "https://au-cdrbanking-pub.wise.com", "https://wise.com/public-resources/assets/logos/wise/brand_logo.svg"),
    ("ME Bank", "me-bank", "https://public.openbank.mebank.com.au/cds-au/v1/banking/products", "https://public.openbank.mebank.com.au", "https://www.mebank.com.au/getmedia/c79ff77e-5b3b-4410-9a1b-98e98a79f025/ME-logo-600px-black-transparent.png"),
    ("Thriday", "thriday", "https://public.cdr.thriday.com.au/cds-au/v1/banking/products", "https://public.cdr.thriday.com.au", "https://assets.website-files.com/61dd1b15c9c40d33f29a4235/61e502fda949f4c2ee4adeb0_Thriday%20Logo_Horizontal%20Full%20Colour-p-500.png"),
    ("HSBC Bank Australia Limited – Wholesale Banking", "hsbc-bank-australia-limited-–-wholesale-banking", "https://public.ob.business.hsbc.com.au/cds-au/v1/banking/products", "https://public.ob.business.hsbc.com.au", "https://www.hsbc.com.au/content/dam/hsbc/au/images/01_HSBC_MASTERBRAND_LOGO_RGB.svg"),
    ("Greater Bank Limited", "greater-bank-limited", "https://public.cdr.greater.com.au/cds-au/v1/banking/products", "https://public.cdr.greater.com.au", "https://www.greater.com.au/globalassets/images/logos/greaterbanklogo.jpg"),
    ("Arab Bank Australia Limited", "arab-bank-australia-limited", "https://public.cdr.arabbank.com.au/cds-au/v1/banking/products", "https://public.cdr.arabbank.com.au", "https://www.arabbank.com.au/themes/arabbank/images/abal-logo.svg"),
    ("Northern Inland Credit Union Limited", "northern-inland-credit-union-limited", "https://secure.nicu.com.au/cds-au/v1/banking/products", "https://secure.nicu.com.au/OpenBanking", "https://nicu.com.au/images/UserUploadedImages/11/NICUlogo.png"),
    ("ME Bank - ME Go", "me-bank---me-go", "https://api.cds.mebank.com.au/cds-au/v1/banking/products", "https://api.cds.mebank.com.au", "https://www.mebank.com.au/getmedia/c79ff77e-5b3b-4410-9a1b-98e98a79f025/ME-logo-600px-black-transparent.png"),
    ("Great Southern Bank Business+", "great-southern-bank-business+", "https://od1.open-banking.business.greatsouthernbank.com.au/cds-au/v1/banking/products", "https://od1.open-banking.business.greatsouthernbank.com.au/api", "https://www.greatsouthernbank.com.au/media/images/global/logo.svg"),
    ("Police Bank", "police-bank", "https://public.cdr.prd.policebank.com.au/cds-au/v1/banking/products", "https://public.cdr.prd.policebank.com.au", "https://www.policebank.com.au/wp-content/uploads/2024/11/Police-Bank-Logo-Base-Primary-2.svg"),
    ("Border Bank", "border-bank", "https://public.cdr.prd.borderbank.com.au/cds-au/v1/banking/products", "https://public.cdr.prd.borderbank.com.au", "https://www.borderbank.com.au/wp-content/uploads/2023/05/BBLogoArtboard-2.png"),
    ("Westpac", "westpac", "https://digital-api.westpac.com.au/cds-au/v1/banking/products", "https://digital-api.westpac.com.au", "https://banking.westpac.com.au/wbc/banking/Themes/Default/Desktop/WBC/Core/Images/logo_white_bg.png.ce5c4c19ec61b56796f0e218fc8329c558421fd8.png"),
    ("NATIONAL AUSTRALIA BANK", "national-australia-bank", "https://openbank.api.nab.com.au/cds-au/v1/banking/products", "https://openbank.api.nab.com.au", "https://www.nab.com.au/etc/designs/nabrwd/clientlibs/images/logo.png"),
    ("ANZ", "anz", "https://api.anz/cds-au/v1/banking/products", "https://api.anz", "https://www.anz.com.au/content/dam/anzcomau/logos/anz/ANZ-MB-Logo-3rd-Party-RGB.png"),
    ("CommBank", "commbank", "https://api.commbank.com.au/public/cds-au/v1/banking/products", "https://api.commbank.com.au/public", "https://www.commbank.com.au/content/dam/commbank-assets/cba-stacked.jpg"),
    ("Regional Australia Bank", "regional-australia-bank", "https://public-data.cdr.regaustbank.io/cds-au/v1/banking/products", "https://public-data.cdr.regaustbank.io", "https://www.regionalaustraliabank.com.au/getcontentasset/ac992c94-0e8c-4439-be38-0028dc45c133/3beffb48-3dfa-48f3-8905-aded8557907a/regional-australia-bank-primary-logo.png?language=en"),
    ("ING BANK (Australia) Ltd", "ing-bank-australia-ltd", "https://id.ob.ing.com.au/cds-au/v1/banking/products", "https://id.ob.ing.com.au", "https://www.ing.com.au/img/logos/ING_Primary_Logo_RGB.png"),
    ("AMP - My AMP", "amp---my-amp", "https://api.cdr-api.amp.com.au/cds-au/v1/banking/products", "https://api.cdr-api.amp.com.au", "https://www.amp.com.au/content/dam/amp-au/data/icons/amp-logo-reversed.svg"),
    ("CommFCU", "commfcu", "https://netbank.communityfirst.com.au/cf-OpenBanking/cds-au/v1/banking/products", "https://netbank.communityfirst.com.au/cf-OpenBanking", "https://cms.communityfirst.com.au/wp-content/uploads/2025/04/CommunityFirstBank-logo-RGB.png"),
    ("Rabobank", "rabobank", "https://openbanking.api.rabobank.com.au/public/cds-au/v1/banking/products", "https://openbanking.api.rabobank.com.au/public", "https://www.rabobank.com.au/content/dam/ranz/ranz-website-images/rbau-images/logo/rb-logo-stacked-200x242px.png"),
    ("Heritage Bank. Please do not use, please use People’s Choice.", "heritage-bank-please-do-not-use-please-use-people’", "https://product.api.heritage.com.au/cds-au/v1/banking/products", "https://product.api.heritage.com.au", "https://www.heritage.com.au/Inbound/Open-Banking/logo"),
    ("Bankwest", "bankwest", "https://open-api.bankwest.com.au/bwpublic/cds-au/v1/banking/products", "https://open-api.bankwest.com.au/bwpublic", "https://www.bankwest.com.au/content/dam/bankwest/system/logos/bankwest-logo-padding.png"),
    ("First Option Bank", "first-option-bank", "https://internetbanking.firstoption.com.au/cds-au/v1/banking/products", "https://internetbanking.firstoption.com.au/OpenBanking", "https://firstoptionbank.com.au/wp-content/uploads/2020/06/FO_Bank_logo_black.png"),
    ("Beyond Bank Australia", "beyond-bank-australia", "https://public.cdr.api.beyondbank.com.au/cds-au/v1/banking/products", "https://public.cdr.api.beyondbank.com.au", "https://brand.beyondbank.com.au/m/1a1424e421d07bea/thul-RGB-GRAD-Beyond-Bank-Logo.png"),
    ("Cairns bank", "cairns-bank", "https://openbanking.cairnsbank.com.au/cds-au/v1/banking/products", "https://openbanking.cairnsbank.com.au/OpenBanking", "https://cairnsbank.com.au/fileadmin/templates/assets/images/cairns-bank-logo.png"),
    ("G&C Mutual Bank", "gandc-mutual-bank", "https://ibank.gcmutualbank.com.au/cds-au/v1/banking/products", "https://ibank.gcmutualbank.com.au/OpenBanking", "https://www.gcmutual.bank/media/3018/gc-mutual-bank-logo.png"),
    ("Teachers Mutual Bank", "teachers-mutual-bank", "https://ob.tmbl.com.au/tmbank/cds-au/v1/banking/products", "https://ob.tmbl.com.au/tmbank", "https://www.tmbank.com.au/-/media/global/logo/desktop/logodesktop.ashx?h=90&w=498&la=en&hash=3CB4B2D2F2C566292E329870B0AE1504"),
    ("Geelong Bank", "geelong-bank", "https://online.geelongbank.com.au/cds-au/v1/banking/products", "https://online.geelongbank.com.au/OpenBanking", "https://geelongbank.com.au/media/2007/geelongbank_logotag_horizontal.png"),
    ("IMB Bank", "imb-bank", "https://openbank.openbanking.imb.com.au/cds-au/v1/banking/products", "https://openbank.openbanking.imb.com.au", "https://uploads-ssl.webflow.com/6523c01e3505e25d762e59e6/66038603eff828b190613f7a_imb-logo.png"),
    ("Suncorp Bank", "suncorp-bank", "https://id-ob.suncorpbank.com.au/cds-au/v1/banking/products", "https://id-ob.suncorpbank.com.au", "https://www.suncorpbank.com.au/content/dam/suncorp/bank/images/logos/suncorp/SuncorpBankVertical_PrimaryRGB_180.png"),
    ("Southern Cross Credit Union", "southern-cross-credit-union", "https://cdr.sccu.com.au/cds-au/v1/banking/products", "https://cdr.sccu.com.au/openbanking", "https://www.sccu.com.au/community/attachment/stacked-logo-cmyk-transparent/"),
    ("Bank of Sydney", "bank-of-sydney", "https://openbank.api.banksyd.com.au/cds-au/v1/banking/products", "https://openbank.api.banksyd.com.au", "https://www.banksyd.com.au/globalassets/images/logos/bos-logo-edge-fix.svg"),
    ("Australian Military Bank", "australian-military-bank", "https://public.open.australianmilitarybank.com.au/cds-au/v1/banking/products", "https://public.open.australianmilitarybank.com.au", "https://www.australianmilitarybank.com.au/sites/default/files/amb_logo_478.png"),
    ("RSL Money", "rsl-money", "https://public.open.rslmoney.com.au/cds-au/v1/banking/products", "https://public.open.rslmoney.com.au", "https://www.rslmoney.com.au/sites/default/files/logo-rslmoney.gif"),
    ("Bank First", "bank-first", "https://public.cdr.bankfirst.com.au/cds-au/v1/banking/products", "https://public.cdr.bankfirst.com.au", "https://cdn.intelligencebank.com/au/share/e3Gq6M/oGkXA/Y01wk/original/Bank+First+Logo+Horizontal+Navy+RGB"),
    ("Up", "up", "https://api.up.com.au/cds-au/v1/banking/products", "https://api.up.com.au", "https://up.com.au/assets/images/logo_1000x1000.png"),
    ("Broken Hill Bank", "broken-hill-bank", "https://public.cdr-api.bhccu.com.au/cds-au/v1/banking/products", "https://public.cdr-api.bhccu.com.au", "https://images.squarespace-cdn.com/content/v1/63fd48114c119156c9e26d0d/d3e7437a-ce6d-4862-9029-5a34ec3350b2/BHB.Colour.Logo.png?format=1500w"),
    ("Bendigo Bank", "bendigo-bank", "https://api.cdr.bendigobank.com.au/cds-au/v1/banking/products", "https://api.cdr.bendigobank.com.au", "https://www.bendigobank.com.au/globalassets/globalresources/brand-logos/bendigobank-logo.png"),
    ("Defence Bank", "defence-bank", "https://product.defencebank.com.au/cds-au/v1/banking/products", "https://product.defencebank.com.au", "https://www.defencebank.com.au/globalassets/images/logos/defence-bank/logo.svg"),
    ("Summerland Bank", "summerland-bank", "https://public.cdr-api.summerland.com.au/cds-au/v1/banking/products", "https://public.cdr-api.summerland.com.au", "https://www.summerland.com.au/app/uploads/2024/02/SB_Logo_NoTagline_Stacked_RGB_BLACK.png"),
    ("Dnister", "dnister", "https://public.cdr-api.dnister.com.au/cds-au/v1/banking/products", "https://public.cdr-api.dnister.com.au", "https://www.dnister.com.au/Signature_Deployment/DnisterLogo.gif"),
    ("Queensland Country Bank", "queensland-country-bank", "https://public.cdr-api.queenslandcountry.bank/cds-au/v1/banking/products", "https://public.cdr-api.queenslandcountry.bank", "https://www.queenslandcountry.bank/siteassets/images/logo-bank/qcb-logo.png"),
    ("Central Murray Bank", "central-murray-bank", "https://secure.cmcu.com.au/cds-au/v1/banking/products", "https://secure.cmcu.com.au/openbanking", "https://www.centralmurray.bank/images/header.png"),
    ("P&N Bank", "pandn-bank", "https://public.cdr-api.pnbank.com.au/cds-au/v1/banking/products", "https://public.cdr-api.pnbank.com.au", "https://digital.pnbank.com.au/globalassets/internet-banking/onboarding/logo-small.png"),
    ("BCU Bank", "bcu-bank", "https://public.cdr-api.bcu.com.au/cds-au/v1/banking/products", "https://public.cdr-api.bcu.com.au", "https://digital.bcu.com.au/globalassets/internet-banking/onboarding/logo-small.png"),
    ("Credit Union SA", "credit-union-sa", "https://openbanking.api.creditunionsa.com.au/cds-au/v1/banking/products", "https://openbanking.api.creditunionsa.com.au", "https://cms.creditunionsa.com.au/assets/images/Open-Banking/cusa-logo_stacked_trans_250px.png"),
    ("Gateway Bank", "gateway-bank", "https://public.cdr-api.gatewaybank.com.au/cds-au/v1/banking/products", "https://public.cdr-api.gatewaybank.com.au", "https://www.gatewaybank.com.au/media/ocrjwsze/gway-logo.png"),
    ("Qudos Bank", "qudos-bank", "https://public.cdr.qudosbank.com.au/cds-au/v1/banking/products", "https://public.cdr.qudosbank.com.au", "https://cdn.prod.website-files.com/663aabca709a328fd2c0ea2e/663b1305def411e0460bafb4_logo-60.svg"),
    ("Fire Service Credit Union", "fire-service-credit-union", "https://public.cdr-api.fscu.com.au/cds-au/v1/banking/products", "https://public.cdr-api.fscu.com.au", "https://www.fscu.com.au/wp-content/uploads//2023/11/FSCU_logo.png"),
    ("MOVE Bank", "move-bank", "https://openbanking.movebank.com.au/cds-au/v1/banking/products", "https://openbanking.movebank.com.au/OpenBanking", "https://movebank.com.au/media/3405/move-bank-logo-website.png"),
    ("St.George Bank", "stgeorge-bank", "https://digital-api.stgeorge.com.au/cds-au/v1/banking/products", "https://digital-api.stgeorge.com.au", "https://www.stgeorge.com.au/content/dam/stg/images/home/STG-logo_1200x1200.jpg"),
    ("BankSA", "banksa", "https://digital-api.banksa.com.au/cds-au/v1/banking/products", "https://digital-api.banksa.com.au", "https://www.banksa.com.au/content/dam/bsa/images/home/BSA-logo_1200x1200.jpg"),
    ("Bank of Melbourne", "bank-of-melbourne", "https://digital-api.bankofmelbourne.com.au/cds-au/v1/banking/products", "https://digital-api.bankofmelbourne.com.au", "https://www.bankofmelbourne.com.au/content/dam/bom/images/home/BOM-logo_1200x1200.jpg"),
    ("RAMS Financial Group Pty Ltd", "rams-financial-group-pty-ltd", "https://digital-api.westpac.com.au/rams/cds-au/v1/banking/products", "https://digital-api.westpac.com.au/rams", "https://www.rams.com.au/siteassets/homepage/rams_logo.png"),
    ("Auswide Bank Ltd", "auswide-bank-ltd", "https://api.auswidebank.com.au/cds-au/v1/banking/products", "https://api.auswidebank.com.au/openbanking", "https://community.auswidebank.com.au/resources/images/templates/shared/auswide-bank-logo.svg"),
    ("UniBank", "unibank", "https://ob.tmbl.com.au/unibank/cds-au/v1/banking/products", "https://ob.tmbl.com.au/unibank", "https://www.unibank.com.au/-/media/unibank/global/_image_/logo/UniBank_RGB_Black_Logo_200x52px.ashx"),
    ("Firefighters Mutual Bank", "firefighters-mutual-bank", "https://ob.tmbl.com.au/fmbank/cds-au/v1/banking/products", "https://ob.tmbl.com.au/fmbank", "https://www.fmbank.com.au/-/media/fmbank/logos/logodesktop.ashx?h=104&w=576&la=en&hash=EC9F95FE23F72341C3F09A087BE117C8"),
    ("Health Professionals Bank", "health-professionals-bank", "https://ob.tmbl.com.au/hpbank/cds-au/v1/banking/products", "https://ob.tmbl.com.au/hpbank", "https://www.hpbank.com.au/-/media/hpbank/logos/hpblogodesktop.ashx?h=520&w=2900&la=en&hash=FB4ACDF35B4BAB4B9AECB37A69160D21"),
    ("Bank Australia", "bank-australia", "https://public.cdr.bankaust.com.au/cds-au/v1/banking/products", "https://public.cdr.bankaust.com.au", "https://www.bankaust.com.au/globalassets/assets/imagery/logos/bank-australia/ba_horizontal_logo.png"),
    ("HSBC", "hsbc", "https://public.ob.hsbc.com.au/cds-au/v1/banking/products", "https://public.ob.hsbc.com.au", "https://www.hsbc.com.au/content/dam/hsbc/au/images/01_HSBC_MASTERBRAND_LOGO_RGB.svg"),
    ("Tyro Payments", "tyro-payments", "https://public.cdr.tyro.com/cds-au/v1/banking/products", "https://public.cdr.tyro.com", "https://www.tyro.com/wp-content/uploads/2021/03/logo1.png"),
    ("Judo Bank", "judo-bank", "https://public.open.judo.bank/cds-au/v1/banking/products", "https://public.open.judo.bank", "https://cdn.unifii.net/judobank/1ddcbc50-08b1-4472-9267-85da3bb20c83.svg"),
    ("Macquarie Bank Limited", "macquarie-bank-limited", "https://api.macquariebank.io/cds-au/v1/banking/products", "https://api.macquariebank.io", "https://www.macquarie.com.au/assets/bfs/global/macquarie-logo_black.svg"),
    ("Card Services", "card-services", "https://api.openbanking.cardservicesdirect.com.au/cds-au/v1/banking/products", "https://api.openbanking.cardservicesdirect.com.au", "https://www.cdn.citibank.com/v1/augcb/cbol/files/images/2021/logo-Card-Services.png"),
    ("Coles Credit Cards", "coles-credit-cards", "https://api.openbanking.secure.coles.com.au/cds-au/v1/banking/products", "https://api.openbanking.secure.coles.com.au", "https://www.coles.com.au/content/dam/coles/coles-financial-services/credit-cards/images/Coles-credit-cards-stacked-logo.png"),
    ("Kogan Money Credit Cards", "kogan-money-credit-cards", "https://api.openbanking.cards.koganmoney.com.au/cds-au/v1/banking/products", "https://api.openbanking.cards.koganmoney.com.au", "https://usl.nab.com.au/static/assets/kogan/img/kogan-money_logo_lg.svg"),
    ("Qantas Money Credit Cards", "qantas-money-credit-cards", "https://api.openbanking.qantasmoney.com/cds-au/v1/banking/products", "https://api.openbanking.qantasmoney.com", "https://assets.qantasmoney.com/logos/qantas-money-logo-sm.svg"),
    ("Aussie Home Loans", "aussie-home-loans", "https://aussie.openportal.com.au/cds-au/v1/banking/products", "https://aussie.openportal.com.au", "https://aussie.openportal.com.au/assets/bfs/applications/digital/ahl/images/aussiehomeloans-logo.png"),
    ("UBank", "ubank", "https://public.cdr-api.86400.com.au/cds-au/v1/banking/products", "https://public.cdr-api.86400.com.au", "https://www.ubank.com.au/assets/images/light/ubank-logo.svg"),
    ("gmcu", "gmcu", "https://secure.gmcu.com.au/cds-au/v1/banking/products", "https://secure.gmcu.com.au/OpenBanking", "https://www.gmcu.com.au/media/2985/gmcu_logo.png"),
    ("Laboratories Credit Union", "laboratories-credit-union", "https://internetbanking.lcu.com.au/cds-au/v1/banking/products", "https://internetbanking.lcu.com.au/OpenBanking", "https://lcu.com.au/wp-content/uploads/2025/03/LCU-LOGO-High-res.png"),
    ("Coastline Bank", "coastline-bank", "https://public.cdr-api.coastline.com.au/cds-au/v1/banking/products", "https://public.cdr-api.coastline.com.au", "https://cdn.sanity.io/images/djf521sf/production/619a4d8c4e9da4c964d2366eeb8ffd143ff37fc1-400x43.png"),
    ("Unity Bank", "unity-bank", "https://ibanking.unitybank.com.au/cds-au/v1/banking/products", "https://ibanking.unitybank.com.au/OpenBanking", "https://ibanking.unitybank.com.au/OpenBanking/logo.png"),
    ("The Capricornian", "the-capricornian", "https://public.cdr.onlinebanking.capricornian.com.au/cds-au/v1/banking/products", "https://public.cdr.onlinebanking.capricornian.com.au", "https://www.capricornian.com.au/app/uploads/2021/08/logo@2x-300x111.png"),
    ("BankVic", "bankvic", "https://ib.bankvic.com.au/cds-au/v1/banking/products", "https://ib.bankvic.com.au/openbanking", "https://ib.bankvic.com.au/bvib/App_Themes/BankVicResponsive/images/BankVic-logo.svg"),
    ("SWSbank", "swsbank", "https://online.swsbank.com.au/cds-au/v1/banking/products", "https://online.swsbank.com.au/openbanking", "https://www.swsbank.com.au/Client_Theme/imgs/logo-desktop.png"),
    ("Citi", "citi", "https://openbanking.api.citi.com.au/cds-au/v1/banking/products", "https://openbanking.api.citi.com.au", "https://www.cdn.citibank.com/v1/augcb/cbol/files/images/2021/logo-Citi.png"),
    ("Family First", "family-first", "https://public.cdr.familyfirst.com.au/cds-au/v1/banking/products", "https://public.cdr.familyfirst.com.au", "https://familyfirst.com.au/wp-content/themes/familyfirst/images/logo.png"),
    ("Police Credit Union Ltd", "police-credit-union-ltd", "https://api.policecu.com.au/cds-au/v1/banking/products", "https://api.policecu.com.au/OpenBanking", "https://www.pcunet1.com.au/internet-banking/App_Themes/PCU-Responsive/images/logo-login.png"),
    ("ORANGE CREDIT UNION LTD", "orange-credit-union-ltd", "https://online.orangecu.com.au/cds-au/v1/banking/products", "https://online.orangecu.com.au/openbanking", "https://online.orangecu.com.au/openbanking/logo.png"),
    ("Illawarra Credit Union Limited", "illawarra-credit-union-limited", "https://onlineteller.cu.com.au/cds-au/v1/banking/products", "https://onlineteller.cu.com.au/OpenBanking", "https://www.illawarracu.com.au/content/themes/nucleo-icu/assets/images/logo.png"),
    ("The Mac", "the-mac", "https://onlinebanking.themaccu.com.au/cds-au/v1/banking/products", "https://onlinebanking.themaccu.com.au/OpenBanking", "https://themaccu.com.au/media/2735/logolb.png"),
    ("Woolworths Team Bank", "woolworths-team-bank", "https://online.woolworthsteambank.com.au/cds-au/v1/banking/products", "https://online.woolworthsteambank.com.au/OpenBanking", "https://woolworthsteambank.com.au/wp-content/uploads/2021/06/wp-log-top-navi-logo.png"),
    ("Australian Unity Bank", "australian-unity-bank", "https://open-banking.australianunity.com.au/cds-au/v1/banking/products", "https://open-banking.australianunity.com.au", "https://www.australianunity.com.au/-/media/rebrandcorporate/logos/au-180years-logo.svg"),
    ("People's Choice", "peoples-choice", "https://ob-public.peopleschoice.com.au/cds-au/v1/banking/products", "https://ob-public.peopleschoice.com.au", "https://www.peopleschoice.com.au/-/media/project/peopleschoice/mainsite/images/brand/600x600_peoples_choice_banking_for_life_logo"),
    ("Easy Street", "easy-street", "https://ebranch.easystreet.com.au/es-OpenBanking/cds-au/v1/banking/products", "https://ebranch.easystreet.com.au/es-OpenBanking", "https://cms.easystreet.com.au/wp-content/uploads/2025/04/Easy-Street-logo.png"),
    ("Maitland Mutual Limited", "maitland-mutual-limited", "https://openbanking.themutual.com.au/cds-au/v1/banking/products", "https://openbanking.themutual.com.au/OpenBanking", "https://openbanking.themutual.com.au/OpenBanking/logo.png"),
    ("Great Southern Bank", "great-southern-bank", "https://api.open-banking.greatsouthernbank.com.au/cds-au/v1/banking/products", "https://api.open-banking.greatsouthernbank.com.au", "https://www.greatsouthernbank.com.au/media/images/global/logo.svg"),
    ("QBANK", "qbank", "https://banking.qbank.com.au/cds-au/v1/banking/products", "https://banking.qbank.com.au/openbanking", "https://www.qbank.com.au/media/logo/qbank-logo.svg"),
    ("Horizon Bank", "horizon-bank", "https://onlinebanking.horizonbank.com.au/cds-au/v1/banking/products", "https://onlinebanking.horizonbank.com.au/openbanking", "https://horizonbank.com.au/Client_Theme/imgs/horizon_logo.png"),
    ("bankWAW", "bankwaw", "https://onlinebanking.wawcu.com.au/cds-au/v1/banking/products", "https://onlinebanking.wawcu.com.au/OpenBanking", "https://onlinebanking.wawcu.com.au/OpenBanking/logo.png"),
    ("Hume Bank", "hume-bank", "https://ibankob.humebank.com.au/cds-au/v1/banking/products", "https://ibankob.humebank.com.au/OpenBanking", "https://ibankob.humebank.com.au/humebank.png"),
    ("Darling Downs Bank", "darling-downs-bank", "https://openbanking.wcu.com.au/cds-au/v1/banking/products", "https://openbanking.wcu.com.au/OpenBanking", "https://www.ddbank.com.au/app/uploads/2025/08/DDB-FinalRGB-01-e1755734579783.png"),
    ("CBA - CommBiz", "cba---commbiz", "https://cdr.commbiz.api.commbank.com.au/cbzpublic/cds-au/v1/banking/products", "https://cdr.commbiz.api.commbank.com.au/cbzpublic", "https://www.commbank.com.au/content/dam/commbank/commBank-logo.svg"),
    ("Bank of us", "bank-of-us", "https://api.bankofus.com.au/cds-au/v1/banking/products", "https://api.bankofus.com.au/OpenBanking", "https://api.bankofus.com.au/OpenBanking/Logo.png"),
    ("TMCU", "tmcu", "https://banking.transportmutual.com.au/cds-au/v1/banking/products", "https://banking.transportmutual.com.au/OpenBanking", "https://banking.transportmutual.com.au/OpenBanking/logo.png"),
    ("Australian Mutual Bank LTD", "australian-mutual-bank-ltd", "https://internetbanking.australianmutual.bank/cds-au/v1/banking/products", "https://internetbanking.australianmutual.bank/openbanking", "https://internetbanking.australianmutual.bank/openbanking/logo.png"),
    ("Bank of Queensland Limited", "bank-of-queensland-limited", "https://api.cds.boq.com.au/cds-au/v1/banking/products", "https://api.cds.boq.com.au", "https://www.boq.com.au/content/dam/boq/images/miscellaneous-images/boq-logo2.png"),
    ("BOQ Specialist", "boq-specialist", "https://api.cds.boqspecialist.com.au/cds-au/v1/banking/products", "https://api.cds.boqspecialist.com.au", "https://www.boqspecialist.com.au/content/dam/boq-specialist/logos/BOQSpecialist_H_CMYK.png"),
    ("DDH Graham", "ddh-graham", "https://api.cds.ddhgraham.com.au/cds-au/v1/banking/products", "https://api.cds.ddhgraham.com.au", "https://ddhgraham.com.au/wp-content/uploads/DDH_BOQ_512.png"),
    ("RACQ Bank", "racq-bank", "https://cdrbank.racq.com.au/cds-au/v1/banking/products", "https://cdrbank.racq.com.au", "https://cdn.intelligencebank.com/au/share/0Mvj/Y0GpK/RqBJZ/original/RACQ-BANK-LOGO_HOR_RGB.png"),
    ("Virgin Money", "virgin-money", "https://api.cds.virginmoney.com.au/cds-au/v1/banking/products", "https://api.cds.virginmoney.com.au", "https://virginmoney.com.au/content/dam/virginmoney/vma-logo.gif"),
    ("Bank of China", "bank-of-china", "https://api-gateway.bankofchina.com.au/cds-au/v1/banking/products", "https://api-gateway.bankofchina.com.au", "https://boc-resources.s3.ap-southeast-2.amazonaws.com/images/BOC+logo.JPG"),
    ("ANZ Plus", "anz-plus", "https://cdr.apix.anz/cds-au/v1/banking/products", "https://cdr.apix.anz", "https://assets.anz.com/is/image/anz/ANZPlus-Logo-Blue?$ResponsiveImage$&fmt=png-alpha"),
    ("Unloan", "unloan", "https://public.api.cdr.unloan.com.au/cds-au/v1/banking/products", "https://public.api.cdr.unloan.com.au", "https://assets.website-files.com/5db407e82f48093c889589aa/610a26bbe635e42da8e03fe8_Unloan_logo.svg"),
    ("Reliance Bank", "reliance-bank", "https://ibanking.reliancebank.com.au/rel-openbanking/cds-au/v1/banking/products", "https://ibanking.reliancebank.com.au/rel-openbanking", "https://ibanking.reliancebank.com.au/rel-openbanking/logo.png"),
    ("Central West CUL", "central-west-cul", "https://ib.cwcu.com.au/cds-au/v1/banking/products", "https://ib.cwcu.com.au/openbanking", "https://ib.cwcu.com.au/OpenBanking/logo.png"),
    ("Heartland", "heartland", "https://api.cdr.heartlandbank.com.au/cds-au/v1/banking/products", "https://api.cdr.heartlandbank.com.au", "https://www.heartlandbank.com.au/images/heartland-bank-logo-white-on-midnight-blue.jpg"),
    ("Newcastle Permanent Building Society", "newcastle-permanent-building-society", "https://openbank.newcastlepermanent.com.au/cds-au/v1/banking/products", "https://openbank.newcastlepermanent.com.au", "https://www.newcastlepermanent.com.au/-/media/images/NPBS-LOGO"),
    ("BNK Bank (Goldfields Money/BCHL)", "bnk-bank-goldfields-money/bchl", "https://public.cdr.bnk.com.au/cds-au/v1/banking/products", "https://public.cdr.bnk.com.au", "https://d26ocd7o1oup8r.cloudfront.net/2019/01/BNK_Logo_RGB_Green-1024x476.png"),
    ("Tyro Banking", "tyro-banking", "https://od1.cdr.banking.tyro.com/cds-au/v1/banking/products", "https://od1.cdr.banking.tyro.com/api", "https://cdn.troy-prod.troy-prod.cxnpl.io/logo/logo.png"),
    ("Solo by MYOB", "solo-by-myob", "https://od1.open-banking.myob.greatsouthernbank.com.au/cds-au/v1/banking/products", "https://od1.open-banking.myob.greatsouthernbank.com.au/api", "https://cdn.moby-prod.prod.cxnpl.io/logo/logoDark.svg"),
    ("in1bank ltd.", "in1bank-ltd", "https://cdr.in1bank.com.au/cds-au/v1/banking/products", "https://cdr.in1bank.com.au", "https://in1bank.com.au/_inc/images/logo.svg"),
    ("Liberty Financial", "liberty-financial", "https://services.liberty.com.au/api/data-holder-public/cds-au/v1/banking/products", "https://services.liberty.com.au/api/data-holder-public", "https://d2ttwt9gu7swv4.cloudfront.net/cdr_assets/Liberty-Aero-Horizontal-RGB.jpg"),
    ("Adelaide Bank", "adelaide-bank", "https://api.cdr.adelaidebank.com.au/cds-au/v1/banking/products", "https://api.cdr.adelaidebank.com.au", "https://www.cdr.gov.au/sites/default/files/2022-08/No-logo-available-2.png"),
    ("Traditional Credit Union", "traditional-credit-union", "https://prd.tcu.com.au/cds-au/v1/banking/products", "https://prd.tcu.com.au", "https://www.cdr.gov.au/sites/default/files/2022-08/No-logo-available-2.png"),
]

def get_bank_endpoints():
    """Get list of (name, brand_id, endpoint) tuples for luke_prior_realtime.py"""
    return [(name, brand_id, endpoint) for name, brand_id, endpoint, _, _ in COMPREHENSIVE_BANK_LIST]

def get_bank_by_name(name):
    """Get bank details by name"""
    for bank in COMPREHENSIVE_BANK_LIST:
        if bank[0] == name:
            return bank
    return None

def get_major_banks():
    """Get the Big 4 + major banks"""
    major_bank_names = ['ANZ', 'CommBank', 'NATIONAL AUSTRALIA BANK', 'Westpac', 
                       'ING BANK (Australia) Ltd', 'Macquarie Bank Limited', 'UBank']
    return [get_bank_by_name(name) for name in major_bank_names if get_bank_by_name(name)]

# Metadata
GENERATION_DATE = '2025-09-17 20:55:23'
TOTAL_BANKS = 120
CDR_REGISTER_URL = 'https://api.cdr.gov.au/cdr-register/v1/all/data-holders/brands/summary'
