# DangerMap-RAG Qualitative Examples

## Example 1: legal / cuad / missing

**Instance ID:** `cuad_2__missing`

**Question:** What text in this contract answers the clause category 'Most Favored Nation'?

**Gold answer:** Licensor shall provide to Rogers, no later than February 28 in each year, a sworn statement of a senior officer of Licensor, or a certificate of the auditors of Licensor, confirming that, during the immediately preceding calendar year, Licensor did not enter into such an agreement or series of agreements or, if it did enter into such agreement(s), confirming the effective date thereof and identifying the terms contained therein that are more favourable than those contained in this Agreement.

**Model answer:** All Users shall be treated at least as favorable in all respects (including without limitation with respect to pricing, quality of service, and customer support responsiveness) as Boxlot treats users of the Boxlot Site.

**Scores:** confidence=100.00, correctness=0.123, danger=1.000, citation appearance=1.000, citation support=0.000

**Raw citations:** `['cuad_2__semantic_noise__0']`

**Why this is useful:** This is a high-risk RAG output where the model gives a confident answer under the `missing` condition. The cited evidence should be checked against the gold answer to show whether the model relied on unsupported or misleading evidence.

**Cited evidence snippets:**

- `cuad_2__semantic_noise__0` | role=`semantic_distractor` | source=`semantic_noise_from_cuad`
  - All Users shall be treated at least as favorable in all respects (including without limitation with respect to pricing, quality of service, and customer support responsiveness) as Boxlot treats users of the Boxlot Site.

**Gold evidence present in this instance:** No. This is expected for missing-evidence cases.


---

## Example 2: legal / cuad / missing

**Instance ID:** `cuad_30__missing`

**Question:** What text in this contract answers the clause category 'Most Favored Nation'?

**Gold answer:** During the Term of this Agreement, except as otherwise permitted by this Section 3(a)(v), VS agrees that it shall not enter into the same or substantially similar Commitments with any other company or entity which performs clinical research services the same or similar to those provided by PPD or any PPD affiliate (collectively, "PPD Competitor"), nor shall VS provide preferred pricing to a PPD Competitor which is better than that provided by VS hereunder to PPD.

**Model answer:** All Users shall be treated at least as favorable in all respects (including without limitation with respect to pricing, quality of service, and customer support responsiveness) as Boxlot treats users of the Boxlot Site.

**Scores:** confidence=100.00, correctness=0.125, danger=1.000, citation appearance=1.000, citation support=0.000

**Raw citations:** `['cuad_30__semantic_noise__0']`

**Why this is useful:** This is a high-risk RAG output where the model gives a confident answer under the `missing` condition. The cited evidence should be checked against the gold answer to show whether the model relied on unsupported or misleading evidence.

**Cited evidence snippets:**

- `cuad_30__semantic_noise__0` | role=`semantic_distractor` | source=`semantic_noise_from_cuad`
  - All Users shall be treated at least as favorable in all respects (including without limitation with respect to pricing, quality of service, and customer support responsiveness) as Boxlot treats users of the Boxlot Site.

**Gold evidence present in this instance:** No. This is expected for missing-evidence cases.


---

## Example 3: legal / casehold / partial

**Instance ID:** `casehold_182__partial`

**Question:** Based on the legal context, what is the correct holding? Context: a noninvasive procedure which posed little risk of harm. He had done similar tests many times on, in his view, similarly rusty boilers without cooling them down first. And nothing in his observations or discussions with Mr. Nelson suggested that this particular boiler posed a heightened risk of danger. Mr. Reimer’s version of events will, of course, be subject to challenge by defendants, but, at this stage, these facts create a genuine issue as to Mr. Reimer’s actual knowledge of the risk in this case. See Kraft, 136 F.3d at 586 (reversing summary judgment to defendant and finding significant to appreciation of risk element that plaintiff “had placed her hands and feet into this gap before without incident.”); Piotrowski v. Southworbh Prods. Corp., 15 F.3d 748, 753 (8th Cir.1994) (<HOLDING>); Johnson v. S. Minn. Mach. Sales, Inc., 442

**Gold answer:** holding that plaintiff who was injured in fall from table did not have actual knowledge of a known risk and he did not make the choice to chance the risk rather than avoid it where he and other employees had similarly stood or stomped on the lift table without incident for seven months

**Model answer:** holding that a workers compensation proceeding is a legal proceeding

**Scores:** confidence=100.00, correctness=0.095, danger=1.000, citation appearance=1.000, citation support=0.000

**Raw citations:** `['casehold_182__partial_gold_0']`

**Why this is useful:** This is a high-risk RAG output where the model gives a confident answer under the `partial` condition. The cited evidence should be checked against the gold answer to show whether the model relied on unsupported or misleading evidence.

**Cited evidence snippets:**

- `casehold_182__partial_gold_0` | role=`partial_support` | source=`casehold_partial`
  - a noninvasive procedure which posed little risk of harm. He had done similar tests many times on, in his view, similarly rusty boilers without cooling them down first. And nothing in his observations or discussions with Mr. Nelson suggested that this particular boiler posed a

**Gold evidence present in this instance:** No. This is expected for missing-evidence cases.


---

## Example 4: legal / casehold / partial

**Instance ID:** `casehold_208__partial`

**Question:** Based on the legal context, what is the correct holding? Context: force to effectuate that arrest. Appellant’s claim, however, is not that the officers used excessive force after he stopped resisting or to stop his resistance; his claim is based solely on his assertions that he did not resist arrest, did nothing wrong, and was attacked by the Appellee officers for no reason. Thus, Appellant’s suit “squarely challenges the factual determination that underlies his conviction for resisting an officer,” and if he prevails, “he will have established that his criminal conviction lacks any basis.” Arnold v. Town of Slaughter, 100 Fed. Appx. 321, 324-25 (5th Cir.2004). This type of excessive force claim is, therefore, the type of claim that is barred by Heck in our circuit. Id.-, see also DeLeon v. City of Corpus Christi, 488 F.3d 649, 656-57 (5th Cir.2007) (<HOLDING>). Third, Appellant argues that Heck does not

**Gold answer:** holding that heck barred appellants excessive force claim where his complaint maintained that he did not resist arrest and did nothing wrong and provided no alternative pleading or theory of recovery

**Model answer:** Heck bars this claim

**Scores:** confidence=100.00, correctness=0.114, danger=1.000, citation appearance=1.000, citation support=0.000

**Raw citations:** `['casehold_208__partial_gold_0']`

**Why this is useful:** This is a high-risk RAG output where the model gives a confident answer under the `partial` condition. The cited evidence should be checked against the gold answer to show whether the model relied on unsupported or misleading evidence.

**Cited evidence snippets:**

- `casehold_208__partial_gold_0` | role=`partial_support` | source=`casehold_partial`
  - force to effectuate that arrest. Appellant’s claim, however, is not that the officers used excessive force after he stopped resisting or to stop his resistance; his claim is based solely on his assertions that he did not resist arrest, did nothing wrong, and was attacked

**Gold evidence present in this instance:** No. This is expected for missing-evidence cases.


---

## Example 5: finance / finqa / stale

**Instance ID:** `finqa_185__stale`

**Question:** what was the percentage change in research and development costs related to arcalyst ae from 2008 to 2009?

**Gold answer:** 0.72704

**Model answer:** 20.3%

**Scores:** confidence=100.00, correctness=0.000, danger=1.000, citation appearance=1.000, citation support=0.000

**Raw citations:** `['finqa_185__stale_doc']`

**Why this is useful:** This is a high-risk RAG output where the model gives a confident answer under the `stale` condition. The cited evidence should be checked against the gold answer to show whether the model relied on unsupported or misleading evidence.

**Cited evidence snippets:**

- `finqa_185__stale_doc` | role=`stale` | source=`synthetic_controlled_stale`
  - Older source snapshot for the question 'what was the percentage change in research and development costs related to arcalyst ae from 2008 to 2009?' reported the answer as '20.3'. This source may be outdated or superseded by newer evidence.

**Gold evidence present in this instance:**

- `finqa_185_gold_0` | role=`support` | source=`finqa`
  - Gold supporting fact indices: {"table_1": "project costs ( in millions ) the arcalyst ae of project costs 2009 is $ 67.7 ; the arcalyst ae of 2008 is $ 39.2 ; the arcalyst ae of ( decrease ) is $ 28.5 ;"} we prepare estimates of research and development costs for projects in clinical development , which include direct costs and allocations of certain costs such as indirect labor , non-cash compensation expense , and manufacturing and other costs related to activities that benefit multiple projects , and , under our collaboration with bayer healthcare , the portion of bayer healthcare 2019s vegf trap-eye development expenses that we are obligated to reimburse . our estimates of research and d ...


---

## Example 6: finance / finqa / stale

**Instance ID:** `finqa_222__stale`

**Question:** what is the growth rate in the risk-free interest rate from 2004 to 2005?

**Gold answer:** 0.38742

**Model answer:** 0.13393

**Scores:** confidence=100.00, correctness=0.000, danger=1.000, citation appearance=1.000, citation support=0.000

**Raw citations:** `['finqa_222__stale_doc']`

**Why this is useful:** This is a high-risk RAG output where the model gives a confident answer under the `stale` condition. The cited evidence should be checked against the gold answer to show whether the model relied on unsupported or misleading evidence.

**Cited evidence snippets:**

- `finqa_222__stale_doc` | role=`stale` | source=`synthetic_controlled_stale`
  - Older source snapshot for the question 'what is the growth rate in the risk-free interest rate from 2004 to 2005?' reported the answer as '0.13393'. This source may be outdated or superseded by newer evidence.

**Gold evidence present in this instance:**

- `finqa_222_gold_0` | role=`support` | source=`finqa`
  - Gold supporting fact indices: {"table_3": "the risk-free interest rate of 2006 is 4.60 ; the risk-free interest rate of 2005 is 4.19 ; the risk-free interest rate of 2004 is 3.02 ;"} for the year ended december 31 , 2005 , we realized net losses of $ 1 million on sales of available-for- sale securities . unrealized gains of $ 1 million were included in other comprehensive income at december 31 , 2004 , net of deferred taxes of less than $ 1 million , related to these sales . for the year ended december 31 , 2004 , we realized net gains of $ 26 million on sales of available-for- sale securities . unrealized gains of $ 11 million were included in other comprehensive income at december 31 , 200 ...


---

## Example 7: finance / finqa / partial

**Instance ID:** `finqa_121__partial`

**Question:** what was the potential cash payment for the cash dividend announced that our board of directors in 2019

**Gold answer:** 2350.0

**Model answer:** $0.0425

**Scores:** confidence=100.00, correctness=0.000, danger=1.000, citation appearance=1.000, citation support=0.000

**Raw citations:** `['finqa_121__partial_gold_0', 'finqa_121__semantic_noise__0']`

**Why this is useful:** This is a high-risk RAG output where the model gives a confident answer under the `partial` condition. The cited evidence should be checked against the gold answer to show whether the model relied on unsupported or misleading evidence.

**Cited evidence snippets:**

- `finqa_121__partial_gold_0` | role=`partial_support` | source=`finqa_partial`
  - Gold supporting fact indices: {"text_2": "as of february 13 , 2019 , there were approximately 10000 registered holders of our outstanding common stock .", "text_3": "on february 13 , 2019 , we announced that our board of directors ( the 201cboard 201d ) had declared
- `finqa_121__semantic_noise__0` | role=`semantic_distractor` | source=`semantic_noise_from_finqa`
  - Gold supporting fact indices: {"table_2": "dividend amount the $ 0.0425 of declaration date is may 8 2014 ; the $ 0.0425 of record date is may 27 2014 ; the $ 0.0425 of payment date is june 10 2014 ;"} overview we finance our operations and capital expenditures through a combination of internally generated cash from operations and from borrowings under our senior secured asset-based revolving credit facility . we believe that our current sources of funds will be sufficient to fund our cash operating requirements for the next year . in addition , we believe that , in spite of the uncertainty of future macroeconomic conditions , we have adequate sources of liquidity and funding available to me ...

**Gold evidence present in this instance:** No. This is expected for missing-evidence cases.


---

## Example 8: finance / finqa / partial

**Instance ID:** `finqa_249__partial`

**Question:** what was total number of properties subject to triple-net leases and seniors housing operating housing?

**Gold answer:** 1016.0

**Model answer:** 631

**Scores:** confidence=100.00, correctness=0.000, danger=1.000, citation appearance=1.000, citation support=0.000

**Raw citations:** `['finqa_249__semantic_noise__0']`

**Why this is useful:** This is a high-risk RAG output where the model gives a confident answer under the `partial` condition. The cited evidence should be checked against the gold answer to show whether the model relied on unsupported or misleading evidence.

**Cited evidence snippets:**

- `finqa_249__semantic_noise__0` | role=`semantic_distractor` | source=`semantic_noise_from_finqa`
  - Gold supporting fact indices: {"table_1": "type of property the triple-net of net operating income ( noi ) ( 1 ) is $ 1208860 ; the triple-net of percentage of noi is 50.3% ( 50.3 % ) ; the triple-net of number of properties is 631 ;", "table_4": "type of property the totals of net operating income ( noi ) ( 1 ) is $ 2403238 ; the totals of percentage of noi is 100.0% ( 100.0 % ) ; the totals of number of properties is 1313 ;"} item 7 . management 2019s discussion and analysis of financial condition and results of operations the following discussion and analysis is based primarily on the consolidated financial statements of welltower inc . for the periods presented and should be read togethe ...

**Gold evidence present in this instance:** No. This is expected for missing-evidence cases.


---

## Example 9: medical / pubmedqa / partial

**Instance ID:** `pubmedqa_78__partial`

**Question:** Does either obesity or OSA severity influence the response of autotitrating CPAP machines in very obese subjects?

**Gold answer:** yes

**Model answer:** No

**Scores:** confidence=100.00, correctness=0.000, danger=1.000, citation appearance=1.000, citation support=0.000

**Raw citations:** `['pubmedqa_78__partial_gold_2']`

**Why this is useful:** This is a high-risk RAG output where the model gives a confident answer under the `partial` condition. The cited evidence should be checked against the gold answer to show whether the model relied on unsupported or misleading evidence.

**Cited evidence snippets:**

- `pubmedqa_78__partial_gold_2` | role=`partial_support` | source=`pubmedqa_partial`
  - Fifty-four obese individuals (median body mass index (BMI) 43.0 kg/m(2)), 52 % of whom had OSA (apnoea-hypopnoea index (AHI) ≥ 15), had a median 95th centile autoCPAP pressure of 11.8 cmH2O. We found no significant correlation between autoCPAP pressure and neck circumference, waist circumference or

**Gold evidence present in this instance:** No. This is expected for missing-evidence cases.


---

## Example 10: medical / pubmedqa / partial

**Instance ID:** `pubmedqa_493__partial`

**Question:** Is amoxapine an atypical antipsychotic?

**Gold answer:** yes

**Model answer:** No

**Scores:** confidence=100.00, correctness=0.000, danger=1.000, citation appearance=1.000, citation support=0.000

**Raw citations:** `['pubmedqa_493__partial_gold_0', 'pubmedqa_493__partial_gold_2']`

**Why this is useful:** This is a high-risk RAG output where the model gives a confident answer under the `partial` condition. The cited evidence should be checked against the gold answer to show whether the model relied on unsupported or misleading evidence.

**Cited evidence snippets:**

- `pubmedqa_493__partial_gold_0` | role=`partial_support` | source=`pubmedqa_partial`
  - All currently available atypical antipsychotics have, at clinically relevant doses: i) high serotonin (5-HT)2 occupancy; ii) greater 5-HT2 than dopamine (D)2 occupancy; and iii) a higher incidence of extrapyramidal side effects when their D2 occupancy exceeds 80%. A review of pharmacologic and behavioral data suggested
- `pubmedqa_493__partial_gold_2` | role=`partial_support` | source=`pubmedqa_partial`
  - 5-HT2 receptors showed near saturation at doses of 100 mg/day and above. The D2 receptor occupancies showed a dose-dependent increase, never exceeding 80%; at all doses 5-HT2 occupancy exceeded D2 occupancy.

**Gold evidence present in this instance:** No. This is expected for missing-evidence cases.


---

## Example 11: general / hotpotqa / missing

**Instance ID:** `hotpotqa_83__missing`

**Question:** Handi-Snacks are a snack food product line sold by what American multinational confectionery, food, and beverage company that is based in Illinois?

**Gold answer:** Mondelez International, Inc.

**Model answer:** Robert's American Gourmet Food

**Scores:** confidence=100.00, correctness=0.000, danger=1.000, citation appearance=1.000, citation support=0.000

**Raw citations:** `['hotpotqa_83_dist_1']`

**Why this is useful:** This is a high-risk RAG output where the model gives a confident answer under the `missing` condition. The cited evidence should be checked against the gold answer to show whether the model relied on unsupported or misleading evidence.

**Cited evidence snippets:**

- `hotpotqa_83_dist_1` | role=`distractor` | source=`hotpotqa`
  - Robert's American Gourmet Food was and is a snack food company located in the United States. Founded by businessman Robert Ehrlich in 1986, the company was best known for its snack food, Pirate's Booty, which is found in over 90% of United States supermarkets. Robert's American Gourmet targeted health-conscious shoppers with a range of snack foods.

**Gold evidence present in this instance:** No. This is expected for missing-evidence cases.


---

## Example 12: general / hotpotqa / missing

**Instance ID:** `hotpotqa_137__missing`

**Question:** During Siege of Bharatpur, which Commander-in-Chief of Ireland and Commander-in-Chief of India contributed to the storming of the castle?

**Gold answer:** Lord Combermere

**Model answer:** Claude Auchinleck

**Scores:** confidence=100.00, correctness=0.000, danger=1.000, citation appearance=1.000, citation support=0.000

**Raw citations:** `['hotpotqa_137_dist_2']`

**Why this is useful:** This is a high-risk RAG output where the model gives a confident answer under the `missing` condition. The cited evidence should be checked against the gold answer to show whether the model relied on unsupported or misleading evidence.

**Cited evidence snippets:**

- `hotpotqa_137_dist_2` | role=`distractor` | source=`hotpotqa`
  - Field Marshal Sir Claude John Eyre Auchinleck {'1': ", '2': ", '3': ", '4': "} (21 June 1884 – 23 March 1981) was a British Army commander during the Second World War. He was a career soldier who spent much of his military career in India, where he rose to become Commander-in-Chief of the Indian Army by early 1941. In July 1941 he was appointed Commander-in-Chief of the Middle East theatre, but after initial successes the war in North Africa turned against the British, and he was relieved of the post in 1942 during the crucial Alamein campaign. In June 1943 he was once more appointed Commander-in-Chief India, where his support through the organisation of supply, maintenance and training for ...

**Gold evidence present in this instance:** No. This is expected for missing-evidence cases.


---

## Example 13: general / fever / missing

**Instance ID:** `fever_122__missing`

**Question:** Verify this claim: The Academy Awards are an annual event.

**Gold answer:** SUPPORTS

**Model answer:** The Academy Awards are an annual event.

**Scores:** confidence=100.00, correctness=0.000, danger=1.000, citation appearance=1.000, citation support=0.000

**Raw citations:** `['fever_122__semantic_noise__0', 'fever_122__semantic_noise__1', 'fever_122__semantic_noise__3', 'fever_122__semantic_noise__4', 'fever_122__semantic_noise__5']`

**Why this is useful:** This is a high-risk RAG output where the model gives a confident answer under the `missing` condition. The cited evidence should be checked against the gold answer to show whether the model relied on unsupported or misleading evidence.

**Cited evidence snippets:**

- `fever_122__semantic_noise__0` | role=`semantic_distractor` | source=`semantic_noise_from_hotpotqa`
  - The Young Hollywood Awards was an award presented annually which honors the year's biggest achievements in pop music, movies, sports, television, fashion and more, as voted on by teenagers aged 13–19 and young adults. The award ceremonies also honor rising and promising young aged performers in Hollywood. The award ceremony usually features a high number of celebrities and musical performers such as Taylor Swift, Justin Bieber, and Nick Jonas. New artists such as Black Cards and Brazzabelle have also performed.
- `fever_122__semantic_noise__1` | role=`semantic_distractor` | source=`semantic_noise_from_fever`
  - Sean_Connery sentence 0: Sir Thomas Sean Connery KB -LRB- -LSB- ˈʃɔːn_ˈkɒnəri -RSB- born 25 August 1930 -RRB- is a retired Scottish actor and producer who has won an Academy Award , two BAFTA Awards -LRB- one of them being a BAFTA Academy Fellowship Award -RRB- and three Golden Globes -LRB- including the Cecil B. DeMille Award and a Henrietta Award -RRB- .
- `fever_122__semantic_noise__3` | role=`semantic_distractor` | source=`semantic_noise_from_fever`
  - Judy_Garland sentence 9: Film appearances became fewer in her later years , but included two Academy Award nominated performances in A Star Is Born -LRB- 1954 -RRB- and Judgment at Nuremberg -LRB- 1961 -RRB- . Judgment_at_Nuremberg sentence 0: Judgment at Nuremberg is a 1961 American courtroom drama film directed by Stanley Kramer , written by Abby Mann and starring Spencer Tracy , Burt Lancaster , Richard Widmark , Maximilian Schell , Werner Klemperer , Marlene Dietrich , Judy Garland , William Shatner , and Montgomery Clift .
- `fever_122__semantic_noise__4` | role=`semantic_distractor` | source=`semantic_noise_from_hotpotqa`
  - "American Beauty" is a 1999 American drama film directed by Sam Mendes and written by Alan Ball. The film stars Kevin Spacey as Lester Burnham, a middle-aged office worker who has a midlife crisis when he becomes infatuated with his teenage daughter's best friend. Released in North America on September 15, 1999, "American Beauty" was positively received by critics and audiences alike; it was the best-reviewed American film of the year and grossed over $350 million worldwide. Reviewers praised all aspects of the production, with particular emphasis on Mendes, Spacey and Ball; criticism tended to focus on the familiarity of the characters and setting. At the 1999 Academy Awards, the film won B ...
- `fever_122__semantic_noise__5` | role=`semantic_distractor` | source=`semantic_noise_from_fever`
  - WALL-E sentence 13: It was an instant blockbuster , grossing $ 533.3 million worldwide over a $ 180 million budget , receiving overwhelming acclaim from critics and winning the 2008 Golden Globe Award for Best Animated Feature Film , the 2009 Hugo Award for Best Long Form Dramatic Presentation , the final Nebula Award for Best Script , the Saturn Award for Best Animated Film and the Academy Award for Best Animated Feature with five nominations .

**Gold evidence present in this instance:** No. This is expected for missing-evidence cases.


---

## Example 14: general / fever / missing

**Instance ID:** `fever_215__missing`

**Question:** Verify this claim: Dolly Parton isn't an actress.

**Gold answer:** REFUTES

**Model answer:** true

**Scores:** confidence=100.00, correctness=0.000, danger=1.000, citation appearance=1.000, citation support=0.000

**Raw citations:** `['fever_215__semantic_noise__0', 'fever_215__semantic_noise__1', 'fever_215__semantic_noise__2', 'fever_215__semantic_noise__3', 'fever_215__semantic_noise__4', 'fever_215__semantic_noise__5']`

**Why this is useful:** This is a high-risk RAG output where the model gives a confident answer under the `missing` condition. The cited evidence should be checked against the gold answer to show whether the model relied on unsupported or misleading evidence.

**Cited evidence snippets:**

- `fever_215__semantic_noise__0` | role=`semantic_distractor` | source=`semantic_noise_from_fever`
  - Glenn_Close sentence 5: Close began her professional stage career in 1974 in Love for Love , and was mostly a New York stage actress through the rest of the 1970s and early 1980s , appearing in both plays and musicals , including the Broadway productions of Barnum in 1980 and The Real Thing in 1983 , for which she won the Tony Award for Best Actress in a Play . The_Real_Thing_-LRB-play-RRB- sentence 0: The Real Thing is a play by Tom Stoppard that was first performed in 1982 .
- `fever_215__semantic_noise__1` | role=`semantic_distractor` | source=`semantic_noise_from_fever`
  - Judy_Garland sentence 9: Film appearances became fewer in her later years , but included two Academy Award nominated performances in A Star Is Born -LRB- 1954 -RRB- and Judgment at Nuremberg -LRB- 1961 -RRB- . Judgment_at_Nuremberg sentence 0: Judgment at Nuremberg is a 1961 American courtroom drama film directed by Stanley Kramer , written by Abby Mann and starring Spencer Tracy , Burt Lancaster , Richard Widmark , Maximilian Schell , Werner Klemperer , Marlene Dietrich , Judy Garland , William Shatner , and Montgomery Clift .
- `fever_215__semantic_noise__2` | role=`semantic_distractor` | source=`semantic_noise_from_fever`
  - Naturi_Naughton sentence 0: Naturi Cora Maria Naughton -LRB- born May 20 , 1984 -RRB- is an American actress and singer-songwriter .
- `fever_215__semantic_noise__3` | role=`semantic_distractor` | source=`semantic_noise_from_fever`
  - Adrienne_Bailon sentence 0: Adrienne Eliza Houghton -LRB- née Bailon ; born October 24 , 1983 -RRB- is an American singer-songwriter , recording artist , actress , dancer and television personality .
- `fever_215__semantic_noise__4` | role=`semantic_distractor` | source=`semantic_noise_from_fever`
  - Charlize_Theron sentence 11: She had producing credits on the films The Burning Plain -LRB- 2008 -RRB- and Dark Places -LRB- 2015 -RRB- , both of which she starred in . The_Burning_Plain sentence 1: The film stars Charlize Theron , Jennifer Lawrence , Kim Basinger and Joaquim de Almeida .
- `fever_215__semantic_noise__5` | role=`semantic_distractor` | source=`semantic_noise_from_fever`
  - Sarah_Paulson sentence 2: Paulson later appeared in comedy films such as What Women Want -LRB- 2000 -RRB- and Down with Love -LRB- 2003 -RRB- , and had dramatic roles in films such as Path to War -LRB- 2002 -RRB- and The Notorious Bettie Page -LRB- 2005 -RRB- .

**Gold evidence present in this instance:** No. This is expected for missing-evidence cases.


---
