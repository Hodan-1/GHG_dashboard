"""
Policy data for different countries in the GHG Emissions Dashboard.
Contains detailed information about climate policies by country and sector.
"""

# Policy data by country
policy_data = {
    'United States of America': {
        'Sectors': {
            'Energy': {
                'description': 'The U.S. is heavily investing in clean energy to decarbonise its grid, primarily through the Inflation Reduction Act (IRA).',
                'policies': [
                    'IRA Tax Credits: Generous tax credits for renewable energy projects (e.g., wind, solar) and technologies like carbon capture and storage (CCS).',
                    'State-level RPS: Many states have their own Renewable Portfolio Standards, mandating a percentage of electricity from renewable sources.',
                ]
            },
            'Industrial Processes & Product Use': {
                'description': 'Policy focuses on providing financial incentives for industrial decarbonisation.',
                'policies': [
                    'IRA Funding: The IRA provides billions in funding for industrial technologies and tax credits for clean hydrogen and CCS deployment.',
                    'AIM Act: The American Innovation and Manufacturing Act phases down the use of hydrofluorocarbons (HFCs), which are potent greenhouse gases.',
                ]
            },
            'Agriculture, Forestry & Other Land Use': {
                'description': 'Policies are aimed at supporting sustainable land management practices and reducing agricultural emissions.',
                'policies': [
                    'IRA Conservation Programs: The IRA allocates significant funding to boost conservation programs and incentivise climate-smart agriculture.',
                    'Biofuels Initiatives: Supports the production and use of biofuels to reduce emissions from the transportation sector.',
                ]
            },
            'Waste': {
                'description': 'Focuses on reducing methane emissions from landfills through collection and use.',
                'policies': [
                    'Landfill Methane Rule: Federal regulations require large landfills to capture methane emissions.',
                ]
            },
        },
        'Subsectors': {
            'Electricity & Heat Generation': {
                'description': 'The IRA is the key driver, providing tax credits for renewable energy projects and carbon capture.',
                'policies': [
                    'IRA Clean Electricity Tax Credits: Provides credits for wind, solar, and other zero-emission technologies.',
                    'Carbon Capture Tax Credits (45Q): Offers significant tax credits for companies that capture and store CO\u2082.',
                ]
            },
            'Road Transport': {
                'description': 'Federal and state policies promote the transition to electric vehicles.',
                'policies': [
                    'EV Tax Credits: Consumers can get up to $7,500 for purchasing new electric vehicles under the IRA.',
                    'CAFE Standards: Federal regulations that mandate increasing fuel efficiency for all vehicles.',
                ]
            },    
            'Buildings': {
                'description': 'Policy efforts focus on improving energy efficiency and promoting electrification through financial incentives.',
                'policies': [
                    'IRA Funding: The IRA provides significant funding for energy efficiency retrofits and rebates for appliances like electric heat pumps.',
                    'Building Performance Standards (BPS): A growing number of states and cities are implementing BPS to set mandatory emissions limits for existing buildings.',
                    'Appliance Standards: The Department of Energy regularly updates efficiency standards for household appliances.',
                ] 
            },
        }
    },
    'United Kingdom': {
        'Sectors': {
            'Energy': {
                'description': 'The UK has rapidly decarbonised its energy sector by phasing out coal and investing in offshore wind.',
                'policies': [
                    'Offshore Wind Target: Aims for 50 GW of offshore wind capacity by 2030.',
                    'Contracts for Difference (CfD): A scheme that provides long-term price certainty for renewable energy investors.',
                ]
            },
            'Industrial Processes & Product Use': {
                'description': 'Policies are focused on industrial decarbonisation and transitioning to low-carbon fuels and technologies.',
                'policies': [
                    'Carbon Pricing: The UK Emissions Trading Scheme (ETS) places a cap and price on carbon, encouraging industries to reduce emissions.',
                    'Industrial Decarbonisation Strategy: A plan to transition to low-carbon fuels (like hydrogen) and technologies in key industrial clusters.',
                ]
            },
            'Agriculture, Forestry & Other Land Use': {
                'description': 'Policies support a move to sustainable farming practices and better land management.',
                'policies': [
                    'Environmental Land Management Schemes (ELMs): Incentivises farmers to adopt environmentally friendly practices.',
                    'Tree Planting Targets: Aims to increase tree cover to absorb more carbon.',
                ]
            },
            'Waste': {
                'description': 'Policy focuses on increasing recycling rates and diverting waste from landfills to reduce methane.',
                'policies': [
                    'Waste and Resources Strategy: Sets targets for higher recycling rates and a move towards a circular economy.',
                ]
            },
        },
        'Subsectors': {
            'Electricity & Heat Generation': {
                'description': 'The UK has successfully phased out coal and is now focused on ramping up renewables.',
                'policies': [
                    'Final Coal Plant Closure: The last coal-fired power plant closed in 2024.',
                    'CfD Auctions: Government-led auctions to secure investment in new renewable energy projects at a set price.',
                ]
            },
            'Road Transport': {
                'description': 'Policies are designed to accelerate the transition to electric vehicles.',
                'policies': [
                    '2035 ICE Ban: A policy to ban the sale of new petrol and diesel cars and vans from 2035.',
                    'Zero Emission Vehicle Mandate: Requires car manufacturers to sell a rising percentage of zero-emission vehicles annually.',
                ]
            },
        }
    },
    'Australia': {
        'Sectors': {
            'Energy': {
                'description': 'The electricity sector is Australia\'s largest source of emissions due to its reliance on coal. Policies are aimed at a rapid transition to renewables.',
                'policies': [
                    'Safeguard Mechanism: Sets emissions limits for Australia\'s largest industrial polluters, requiring them to reduce emissions or buy offsets.',
                    'Capacity Investment Scheme (CIS): Provides revenue certainty for new clean energy projects.',
                ]
            },
            'Industrial Processes & Product Use': {
                'description': 'Policies are focused on managing emissions from industry and chemical processes.',
                'policies': [
                    'Safeguard Mechanism: Covers industrial facilities, encouraging them to invest in emissions reduction technologies.',
                ]
            },
            'Agriculture, Forestry & Other Land Use': {
                'description': 'Policy provides incentives for farmers to adopt sustainable practices and sequester carbon.',
                'policies': [
                    'Carbon Farming Initiative: Supports farmers in undertaking projects to reduce emissions or store carbon in the landscape.',
                    'National Methane Program: Initiatives aimed at reducing methane from livestock through improved feed and management.',
                ]
            },
            'Waste': {
                'description': 'Policies focus on landfill gas capture and improved waste management.',
                'policies': [
                    'Landfill Gas Capture: Regulations and incentives to capture methane from landfills for energy generation.',
                ]
            },
        },
        'Subsectors': {
            'Electricity & Heat Generation': {
                'description': 'The Capacity Investment Scheme is a key tool for accelerating the transition away from coal.',
                'policies': [
                    'Capacity Investment Scheme (CIS): Provides a government-backed revenue floor for new clean energy projects.',
                    'State Renewable Energy Zones: State-level initiatives to build out infrastructure for large-scale solar and wind projects.',
                ]
            },
            'Road Transport': {
                'description': 'Policies are focused on encouraging the uptake of electric vehicles.',
                'policies': [
                    'EV Subsidies and Tax Breaks: Provides financial incentives for purchasing EVs.',
                ]
            },
            'Heavy Industry': {
                'description': 'This subsector is a major source of emissions, particularly from mining and mineral processing.',
                'policies': [
                    'Strengthened Safeguard Mechanism: Sets declining emissions limits for the country\'s largest industrial emitters.',
                ]
            },
        }
    },
    'Ukraine': {
        'Sectors': {
            'Energy': {
                'description': 'Climate policy is heavily influenced by EU accession and the need for green post-war reconstruction.',
                'policies': [
                    'EU Alignment: Adopting EU climate and energy policies as part of its path to joining the European Union.',
                    'Green Reconstruction: Plans to rebuild a decentralised, modern energy grid with a higher share of renewables to improve energy security.',
                ]
            },
            'Industrial Processes & Product Use': {
                'description': 'Focuses on improving energy efficiency in industry and reducing emissions from processes.',
                'policies': [
                    'Energy Efficiency Fund: A state-run program that provides financial support for businesses to implement energy-saving measures.',
                ]
            },
            'Agriculture, Forestry & Other Land Use': {
                'description': 'Policies focus on sustainable farming and improving waste management in the agricultural sector.',
                'policies': [
                    'Land Management Initiatives: Promotes sustainable land use to combat degradation and support biodiversity.',
                    'Biomass for Energy: Incentives for using agricultural waste for energy generation.',
                ]
            },
            'Waste': {
                'description': 'Policies aim to modernise waste management to reduce methane emissions.',
                'policies': [
                    'National Waste Management Strategy: Aims to improve waste collection and processing, including better landfill gas management.',
                ]
            },
        },
        'Subsectors': {
            'Electricity & Heat Generation': {
                'description': 'Policies promote a shift to renewable energy and a more resilient, decentralised grid.',
                'policies': [
                    'Green Tariff: A feed-in tariff system that encourages investment in renewable energy projects.',
                    'Grid Modernisation: Post-war reconstruction efforts prioritise a modern, decentralised grid.',
                ]
            },
            'Road Transport': {
                'description': 'Policies are aimed at promoting the use of electric vehicles and alternative fuels.',
                'policies': [
                    'EV Subsidies: Provides incentives for the purchase of electric vehicles.',
                ]
            },
        }
    },
    'Austria': {
        'Sectors': {
            'Energy': {
                'description': 'Austria is a leader in renewable electricity, with a goal of achieving 100% renewable electricity by 2030.',
                'policies': [
                    'Renewable Energy Expansion Act: Sets a target of adding 27 TWh of renewable electricity by 2030.',
                    'EU ETS: As an EU member, heavy industry and power sectors are covered by the EU Emissions Trading System.',
                ]
            },
            'Industrial Processes & Product Use': {
                'description': 'Policies are tied to EU-wide regulations and domestic support for green technologies.',
                'policies': [
                    'EU ETS: Regulates emissions for large industrial facilities.',
                    'Green Industrial Strategy: Initiatives to promote clean technologies and processes, such as green hydrogen.',
                ]
            },
            'Agriculture, Forestry & Other Land Use': {
                'description': 'Policies focus on sustainable agriculture and the preservation of natural landscapes.',
                'policies': [
                    'Adaptation Strategy: The Austrian Strategy for Adaptation to Climate Change includes specific measures for the agricultural sector.',
                    'Biofuels Mandate: Policies that require a certain percentage of transport fuels to be sourced from biofuels.',
                ]
            },
            'Waste': {
                'description': 'Austria has achieved significant emissions reductions in this sector through improved management and recycling.',
                'policies': [
                    'Waste Management Strategy: Continuous improvement in waste collection and recycling to divert waste from landfills.',
                ]
            },
        },
        'Subsectors': {
            'Electricity & Heat Generation': {
                'description': 'The country leverages its vast hydropower and biomass resources to achieve high levels of renewable energy.',
                'policies': [
                    'Hydropower Investment: Ongoing investment in hydropower, a major source of renewable energy.',
                    'Renewable Energy Act: Provides financial support and a legal framework for renewable energy development.',
                ]
            },
            'Road Transport': {
                'description': 'Policies aim to shift people away from private cars and towards public transport and EVs.',
                'policies': [
                    'Climate Ticket: An affordable, nationwide public transport pass.',
                    'EV Subsidies: Provides financial incentives for the purchase of electric vehicles and charging infrastructure.',
                ]
            },
            'Bioeconomy': {
                'description': 'Policy promotes a transition away from fossil-based products towards a circular economy that uses agricultural and forestry resources sustainably.',
                'policies': [
                    'Austrian Bioeconomy Strategy: A national strategy that aims to replace fossil-based materials and products with renewable ones.',
                ]
            },
            'Methane Strategy': {
                'description': 'Austria has specific policies to address methane emissions, particularly from the agricultural and waste sectors.',
                'policies': [
                    'Waste Management Strategy: Continued efforts to divert organic waste from landfills to reduce methane emissions.',
                    'Methane Reduction Measures in Agriculture: Initiatives to improve livestock management and promote a more sustainable food system.',
                ]
            },
        }
    },

    'Canada': {
        'Sectors': {
            'Energy': {
                'description': 'Canada\'s energy sector is its largest source of emissions. Policy is focused on carbon pricing, methane regulations, and shifting to a cleaner electricity grid.',
                'policies': [
                    'Carbon Pricing: A federal system (or provincial equivalent) places a price on carbon pollution. Revenue from the consumer fuel charge is mostly returned to households through the Canada Carbon Rebate.',
                    'Oil and Gas Emissions Cap: The federal government is developing a cap-and-trade system to limit and reduce emissions from the oil and gas sector.',
                ]
            },
            'Industrial Processes & Product Use': {
                'description': 'Policy uses carbon pricing and a cap-and-trade system to drive industrial decarbonisation and encourage investment in clean technologies.',
                'policies': [
                    'Output-Based Pricing System (OBPS): A federal system for large industrial emitters that sets emissions limits. Emitters that exceed the limit must pay a charge, while those that emit less can generate credits.',
                    'Carbon Capture, Utilisation and Storage (CCUS) Tax Credit: A refundable tax credit for capital costs of CCUS projects, incentivising industrial decarbonisation.',
                ]
            },
            'Agriculture, Forestry & Other Land Use': {
                'description': 'Policies are aimed at supporting farmers in adopting sustainable practices and leveraging land for carbon sequestration.',
                'policies': [
                    'Agricultural Clean Technology Program: Funds the adoption of clean technologies and practices to reduce emissions on farms.',
                    'Two Billion Trees Program: A commitment to plant two billion trees over a decade to help with carbon sequestration.',
                ]
            },
            'Waste': {
                'description': 'Policy is focused on reducing methane emissions from landfills through regulations and improved waste management.',
                'policies': [
                    'Landfill Methane Regulations: Federal regulations to reduce methane emissions from landfills by requiring gas collection and control systems.',
                ]
            },
            'Other': {
                'description': 'This sector includes emissions from other sources not covered in the main categories.',
                'policies': []
            }
        },
        'Subsectors': {
            'Electricity & Heat Generation': {
                'description': 'The country has a goal to achieve a net-zero electricity grid by 2035 through a mix of regulations and financial incentives.',
                'policies': [
                    'Clean Electricity Regulations: Proposed regulations that will limit carbon emissions from electricity generation, effectively requiring the phase-out of fossil fuel-based power plants by 2035.',
                    'Coal Phase-out: A national phase-out of traditional coal-fired electricity by 2030.',
                ]
            },
            'Road Transport': {
                'description': 'Policies are designed to increase the use of low-carbon fuels and accelerate the transition to electric vehicles.',
                'policies': [
                    'Clean Fuel Regulations: Requires gasoline and diesel suppliers to reduce the carbon intensity of their fuels, providing incentives for the use of cleaner fuels like biofuels, electricity, and hydrogen.',
                    'EV Sales Mandate: A federal mandate that requires all new light-duty vehicles sold in Canada to be zero-emission vehicles by 2035.',
                ]
            },
            'Oil & Gas': {
                'description': 'Canada\'s oil and gas sector is the single largest source of the country\'s greenhouse gas emissions. Policies target both methane and carbon dioxide.',
                'policies': [
                    'Methane Regulations: Regulations aim to reduce methane emissions from the oil and gas sector by 75% by 2030.',
                    'Oil and Gas Emissions Cap: Proposed cap-and-trade system to set an absolute limit on emissions from this sector.',
                    'Carbon Capture, Utilisation and Storage (CCUS) Tax Credit: Incentivises the high capital costs associated with CCUS projects for industrial decarbonisation.',
                ]
            },
            'Buildings': {
                'description': 'Emissions from heating and cooling residential, commercial, and institutional buildings are a key focus for decarbonisation.',
                'policies': [
                    'Green Buildings Strategy: A national strategy to accelerate the transition to net-zero-emissions buildings, including energy efficiency retrofits.',
                    'Net-Zero-Ready Building Codes: Working with provinces and territories to implement new model building codes that require highly energy-efficient construction.',
                ]
            },
            'Heavy Industry': {
                'description': 'This subsector includes carbon-intensive industries like mining, smelting, and manufacturing.',
                'policies': [
                    'Output-Based Pricing System (OBPS): The core policy for heavy industry that applies a carbon price to emissions above a certain limit.',
                    'Industrial Decarbonisation Funding: Federal and provincial funds, like the Strategic Innovation Fund, support industrial projects that are deploying clean technologies.',
                    'Carbon Border Adjustment Mechanism (CBAM): Canada is considering a CBAM to place a levy on high-carbon goods imported from countries with weaker climate policies to protect domestic industries.',
                ]
            },
        }
    }
}
