# DangerMap-RAG V3 Manual Perturbation Audit

Review criterion:

- **clean**: sufficient support is present; no artificial distractor.
- **missing**: decisive support is absent.
- **partial**: topical/original support remains, but decisive support is removed.
- **noisy**: sufficient gold support remains despite irrelevant semantic distractors.
- **contradictory**: genuine-looking evidence supports incompatible answers without an explicit conflict cue.
- **stale**: only an older answer-bearing snapshot is available, without explicit 'stale/outdated' wording.

## Case 01: casehold / clean

**Instance ID:** `casehold_3695__clean`

**Question:** Which holding is best supported by the retrieved legal context? Choose one option. Options: A) holding that rule 415f worked to cure deficiencies in service of process in action to enforce a judgment lien on real estate where service was provided at debtors last residential address known to lienholder because address was used during underlying lawsuit lienholders attorney checked county record to verify address information debtor did receive summons and residential address was on the former situs of debtors business B) holding that a correct address could have been determined by checking telephone directory C) holding that considering an amendment is not the time to address the merits of a case D) holding that adts failure to dispatch ems to correct address was not actionable in tort E) holding that trial court did not abuse its discretion in refusing to require disclosure of witness address because personal safety exception applied noting that defendant knew victims prior address thereby limiting value of victims most current address

**Gold answer:** holding that adts failure to dispatch ems to correct address was not actionable in tort

**Expected abstention:** False

**Evidence:**

### Document 1

- ID: `casehold_3695_gold_0`
- Role: `support`
- Source: `casehold`
- Title: CaseHOLD legal context

the parties have contracted directly, such a duty may arise if one party’s conduct “creates a new hazard” resulting from something more than nonperformance. See Fultz, 683 N.W.2d at 592-93; see also Hill, 822 N.W.2d at 202. Some older cases draw a distinction between nonfeasance and misfeasance, finding only the latter to be actionable in tort, but this approach has largely been supplanted by the “separate and distinct” and “new hazard” standards. See Fultz, 683 N.W.2d at 592 (“[T]he former misfeasance/nonfeasance inquiry ... is defective because it improperly focuses on whether a duty was breached instead of whether a duty exists at all.”). Under Michigan law, ADT did not owe Ram a statutory or common-law duty to detect the burglary or dispatch police. See Spengler, 505 F.3d at 458 (<HOLDING>); see also Hill, 822 N.W.2d at 196 (no common

**Human judgment:** PASS / FAIL / UNCERTAIN

**Reason:**

---

## Case 02: casehold / contradictory

**Instance ID:** `casehold_1418__contradictory`

**Question:** Which holding is best supported by the retrieved legal context? Choose one option. Options: A) holding that bankruptcy court is without jurisdiction to control disposition of chapter 13 debtors property that is not property of the bankruptcy estate unless the property is related to the bankruptcy proceedings of the code B) holding that the texas proceeds rule is only applicable in a chapter 13 bankruptcy case and would not apply where the debtor sells homestead property postpetition in a chapter 7 bankruptcy case C) holding that facts as they existed on the date of the original bankruptcy petition not on the date of conversion from chapter 13 to chapter 7 bankruptcy applied D) holding that the 1994 amendment to 348 of the bankruptcy code should control in preamendment ongoing cases and that the debtors tort causes of action that accrued while the case was proceeding under chapter 13 did not become property of the estate or subject to the bankruptcy proceedings upon conversion of the case to chapter 7 proceedings E) holding that funds held by chapter 13 trustee become property of the chapter 7 estate upon conversion not subject to exemption

**Gold answer:** holding that the 1994 amendment to 348 of the bankruptcy code should control in preamendment ongoing cases and that the debtors tort causes of action that accrued while the case was proceeding under chapter 13 did not become property of the estate or subject to the bankruptcy proceedings upon conversion of the case to chapter 7 proceedings

**Expected abstention:** True

**Evidence:**

### Document 1

- ID: `casehold_1418_gold_0`
- Role: `support`
- Source: `casehold`
- Title: CaseHOLD legal context

clearly erroneous findings of fact, carefully and correctly set out the law governing the issues raised, and clearly articulate the reasons underlying the decisions, issuance of a full written opinion by this court would serve no useful purpose. Accordingly, for the reasons stated in the opinions of the magistrate judge and the district court, we AFFIRM. We add only that, although we agree with the magistrate judge’s conclusion that because the trustee in Sharp’s bankruptcy abandoned any interest in this cause of action, Sharp has standing to bring this action and to represent the class, we would find that Sharp has standing principally on the ground that Sharp’s interest in this action was never the property of the bankruptcy estate. See In re Young, 66 F.3d 376, 378-79 (1st Cir.1995)

### Document 2

- ID: `casehold_1418__contradictory_doc`
- Role: `contradictory`
- Source: `synthetic_controlled_contradiction_v3`
- Title: Independent retrieved record

Question recorded: Which holding is best supported by the retrieved legal context? Choose one option. Options: A) holding that bankruptcy court is without jurisdiction to control disposition of chapter 13 debtors property that is not property of the bankruptcy estate unless the property is related to the bankruptcy proceedings of the code B) holding that the texas proceeds rule is only applicable in a chapter 13 bankruptcy case and would not apply where the debtor sells homestead property postpetition in a chapter 7 bankruptcy case C) holding that facts as they existed on the date of the original bankruptcy petition not on the date of conversion from chapter 13 to chapter 7 bankruptcy applied D) holding that the 1994 amendment to 348 of the bankruptcy code should control in preamendment ongoing cases and that the debtors tort causes of action that accrued while the case was proceeding under chapter 13 did not become property of the estate or subject to the bankruptcy proceedings upon conversion of the case to chapter 7 proceedings E) holding that funds held by chapter 13 trustee become property of the chapter 7 estate upon conversion not subject to exemption Reported answer: holdin ...

### Document 3

- ID: `casehold_1418__semantic_noise__0`
- Role: `semantic_distractor`
- Source: `semantic_noise_from_casehold`
- Title: CaseHOLD legal context

of the legislative history behind § 544(a)). The Bankruptcy Code does not authorize the Trustee to collect property or money except that which is owed to the estate. 2. The Trustee alternatively contends that the conspiracy claim belongs to the bankruptcy estate because, unlike in Caplin, the claim here seeks to remedy an injury to all of Bradley’s creditors and not merely a subset thereof. Even assuming that any or all of Bradley’s creditors could properly assert the claim, we disagree that this fact alone confers standing on the Trustee. This court recently clarified that, when determining whether a claim is property of the bankruptcy estate such that the trustee has standing to assert it under 11 U.S.C. § 541(a), the distinction between claims that 52-53 (5th Cir.1987) (<HOLDING>). But Texas law does not suggest that Bradley

### Document 4

- ID: `casehold_1418__semantic_noise__1`
- Role: `semantic_distractor`
- Source: `semantic_noise_from_casehold`
- Title: CaseHOLD legal context

rights “should be valued as an inherent part of his property interest”). We are persuaded that the first line of cases correctly interprets the statute. This interpretation gives meaning to both sentences of § 506(a), and enables bankruptcy courts to exercise the flexibility Congress intended. By retaining collateral, a Chapter 11 debtor is ensuring that the very event Winthrop proposes to use to value the property — a foreclosure sale — will not take place. At the same time, the debtor should not be heard to argue that, in valuing the collateral, the court should disregard the very event that, according to the debtor’s plan, will take place — namely, the debtor’s use of the collateral to generate an income stream. In ordinary circumstances the present value of the income strea 993) (<HOLDING>); In re Green, 151 B.R. 501 (Bankr.D.Minn.1993)

**Human judgment:** PASS / FAIL / UNCERTAIN

**Reason:**

---

## Case 03: casehold / missing

**Instance ID:** `casehold_1602__missing`

**Question:** Which holding is best supported by the retrieved legal context? Choose one option. Options: A) holding that suppression by prosecutor of evidence favorable to an accused violates due process where evidence is material to either guilt or punishment B) holding that suppression by prosecution of evidence favorable to the accused upon request by the defense violates due process where evidence is material either to guilt or punishment irre spective of the good faith of the prosecution C) holding that suppression of evidence by the prosecution of evidence favorable to the defendant upon request violates the defendants right to due process where the evidence is material D) holding that suppression of evidence favorable to an accused upon request violates due process when evidence is material either to guilt or to punishment irrespective of the good faith or bad faith of the prosecution E) holding that suppression by government of evidence favorable to accused upon request violates due process when evidence is material to guilt

**Gold answer:** holding that suppression of evidence favorable to an accused upon request violates due process when evidence is material either to guilt or to punishment irrespective of the good faith or bad faith of the prosecution

**Expected abstention:** True

**Evidence:**

### Document 1

- ID: `casehold_1602__semantic_noise__0`
- Role: `semantic_distractor`
- Source: `semantic_noise_from_casehold`
- Title: CaseHOLD legal context

is to examine, in light of agistrate in issuing search warrant “is to make a practical, common sense decision whether, given all the circumstances set forth in the warrant’s supporting affidavit, including the veracity and basis of knowledge of persons supplying hearsay information, there is a fair probability that contraband or evidence of a crime will be found in a particular place”). However, when an affidavit in support of a search warrant based on information obtained from an informant fails to state when the affiant received the information from the informant, when the informant obtained his information, or when the incident described took place, the affidavit is inadequate to support the issuance of a search warrant. See Schmidt v. State, 659 S.W.2d 420, 421 (Tex.Crim.App.1983) (<HOLDING>). Here, Officer Brinson’s affidavit supporting

### Document 2

- ID: `casehold_1602__semantic_noise__1`
- Role: `semantic_distractor`
- Source: `semantic_noise_from_casehold`
- Title: CaseHOLD legal context

Court may not dismiss the Plaintiff’s Complaint absent a showing of exceptional circumstances. See, e.g., Herbstein, 743 F.Supp. at 188 (finding Argentine case was at preliminary stage where formal investigation into possible misappropriation had just begun and there had not yet been any determination of actual wrongdoing). The Defendant by the Swiss District Court regarding Pablo’s liability on Ms. Madanes’ contractual claim would not dispose of the RICO claims in this action. For example, determining that Pablo is guilty on the contractual claim does not answer the question of whether he managed an international conspiracy; nor does a finding of innocence necessarily mean that no such conspiracy existed, especially among the other Defendants. See id.; Herbstein, 743 F.Supp. at 188 (<HOLDING>). The principal cases upon which the Defendants

### Document 3

- ID: `casehold_1602__semantic_noise__2`
- Role: `semantic_distractor`
- Source: `semantic_noise_from_casehold`
- Title: CaseHOLD legal context

125 L.Ed.2d 209 (1993). The Supreme Court held in Buckley that a prosecutor is not absolutely immune when he allegedly fabricated evidence during the investigation by retaining a dubious expert witness. Id. at 273-75, 113 S.Ct. 2606. The Court reasoned that “[t]here is a difference between the advocate’s role in evaluating evidence and interviewing witnesses as he prepares for trial, ... and the detective’s role in searching for the clues and corroboration that might give him probable cause to recommend that a suspect be arrested....” Id. at 273, 113 S.Ct. 2606 (citations omitted). Because the prosecutor’s conduct in Buckley fell within the latter category, the Supreme Court denied absolute immunity. See also Malley v. Briggs, 475 U.S. 335, 342-43, 106 S.Ct. 1092, 89 L.Ed.2d 271 (1986) (<HOLDING>). In the present case, the District Attorney

### Document 4

- ID: `casehold_1602__semantic_noise__3`
- Role: `semantic_distractor`
- Source: `semantic_noise_from_casehold`
- Title: CaseHOLD legal context

was conscious of the confinement, (3) the plaintiff did not contest the confinement, and (4) the confinement was not otherwise privileged.” Broughton v. State, 37 N.Y.2d 451, 456, 373 N.Y.S.2d 87, 335 N.E.2d 310 (1975), cert. denied, 423 U.S. 929, 96 S.Ct. 277, 46 L.Ed.2d 257 (1975) (internal citations omitted). The only element in dispute in the instant case is the last element — defendant argues that the arrest was privileged as a matter of law because it was supported by probable cause. Fulton v. Robinson, 289 F.3d 188, 195 (2d. Cir.2002) (“A § 1983 claim of false arrest based on the Fourth Amendment right to be free from unreasonable seizures may not be maintained if there was probable cause for the arrest”); see also Bernard v. United States, 25 F.3d 98, 102 (2d Cir. 1994) (<HOLDING>); Cameron v. Fogarty, 806 F.2d 380, 387 (2d

### Document 5

- ID: `casehold_1602__semantic_noise__4`
- Role: `semantic_distractor`
- Source: `semantic_noise_from_casehold`
- Title: CaseHOLD legal context

outcome of the plea process.” Id. At the evidentiary hearing on his motion, Movant made no assertions that his trial counsel failed to adequately explain the charges against him or failed to object to the factual basis underlying his plea. In fact, in his testimony at the evi-dentiary hearing, Movant asserted his trial counsel wrongly advised him to plead guilty because she had failed to investigate three potential witnesses and she failed to explore certain issues relating to one of the victim’s in his case. Accordingly, the issue raised in Movant’s point relied on was not presented to the motion court in his Rule 24.035 motion and cannot be raised for the first time on appeal. Day v. State, 208 S.W.3d 294, 295 (Mo.App.2006); see Amrine v. State, 785 S.W.2d 531, 535 (Mo. banc 1990) (<HOLDING>). Moreover, plain error review is not available

### Document 6

- ID: `casehold_1602__semantic_noise__5`
- Role: `semantic_distractor`
- Source: `semantic_noise_from_casehold`
- Title: CaseHOLD legal context

may recommend a particular sentence based upon the facts before the court. As part of a plea agreement, the Government is free to negotiate away any right it may have to recommend a sentence. However, the Government does not have a right to make an agreement to stand mute in the face of factual inaccuracies or to withhold relevant factual information from the court. Such an agreement not only violates a prosecutor’s duty to the court but would result in sentences based upon incomplete facts or factual inaccuracies, a notion that is simply abhorrent to our legal system. 660 F.2d 1086, 1090-92 (5th Cir.1981) (citations and footnotes omitted). The reasoning of Block has been adopted by the Fourth Circuit as well. E.g., United States v. Perrera, 842 F.2d 73, 75 (4th Cir.1988) (per curiam) (<HOLDING>); United States v. Dail, 1991 WL 631 at *2,

### Document 7

- ID: `casehold_1602__semantic_noise__6`
- Role: `semantic_distractor`
- Source: `semantic_noise_from_casehold`
- Title: CaseHOLD legal context

As noted in the Advisory Committee notes to Rule 41(e) of the Federal Rules of Criminal Procedure, the district court has jurisdiction to hear motions “to compel [the] return of property obtained by an illegal search and seizure.” Fed. R.Crim.P. 41(e) advisory committee’s note. Moreover, the Third Circuit has found that its district courts have jurisdiction over third party motions for the return of property, see United States v. Frank, 763 F.2d 551, 552 (3d Cir.1985) (stating that the district court had jurisdiction to entertain a third party motion to determine who had entitlement to evidence after the criminal prosecution concluded), and that such jurisdiction exists even after the termination of the criminal proceedings, see United States v. McGlory, 202 F.3d 664, 670 (3d Cir.2000) (<HOLDING>); Bein, 214 F.3d at 411 (finding that “[a]

### Document 8

- ID: `casehold_1602__semantic_noise__7`
- Role: `semantic_distractor`
- Source: `semantic_noise_from_casehold`
- Title: CaseHOLD legal context

their arguments to the jury.” State v. Miller, 271 N.C. 646, 659, 157 S.E.2d 335, 346 (1967). Further, the control of counsel’s arguments “must be left largely to the discretion of the trial judge,” State v. Johnson, 298 N.C. 355, 369, 259 S.E.2d 752, 761 (1979), because the trial judge ‘sees what is done, and hears what is said. He is cognizant of all the surrounding circumstances, and is a better judge of the lati tude that ought to be allowed to counsel in the argument of any particular case.’ State v. Thompson, 278 N.C. 277, supporting the jury’s verdict notwithstanding improper characterizations regarding the veracity of witnesses’ statements has been sufficient in some cases to prevent the imposition of a new trial. See e.g. State v. Sexton, 336 N.C. 321, 444 S.E.2d 879 (1994) (<HOLDING>); Thompson, 278 N.C. at 277, 179 S.E.2d at 315

**Human judgment:** PASS / FAIL / UNCERTAIN

**Reason:**

---

## Case 04: casehold / noisy

**Instance ID:** `casehold_2345__noisy`

**Question:** Which holding is best supported by the retrieved legal context? Choose one option. Options: A) recognizing that the iirira strips the court of jurisdiction over the attorney generals discretionary extreme hardship determination but retaining jurisdiction over constitutional due process claims B) recognizing that failure to exhaust an issue before the bia strips us of jurisdiction C) holding that the court of federal claims lacked jurisdiction over claims arising from the violation of a criminal statute D) holding that the court of appeals has jurisdiction to decide its jurisdiction under the transitional rules of the iirira E) holding over

**Gold answer:** recognizing that the iirira strips the court of jurisdiction over the attorney generals discretionary extreme hardship determination but retaining jurisdiction over constitutional due process claims

**Expected abstention:** False

**Evidence:**

### Document 1

- ID: `casehold_2345_gold_0`
- Role: `support`
- Source: `casehold`
- Title: CaseHOLD legal context

Hector Estuardo Zavala Archila (“Zavala”) is a native and citizen of Guatemala. Zavala appeals the Board of Immigration Appeals’ (“BIA”) denial of his application for suspension of deportation. While we lack jurisdiction over the BIA’s discretionary determinations, we have jurisdiction over Zavala’s due process challenge to the BIA’s failure to fully and properly consider the evidence supporting a finding of extreme hardship. See Torres-Aguilar v. INS, 246 F.3d 1267, 1270-71 (9th Cir.2001) (<HOLDING>). We grant the petition and remand to the BIA

### Document 2

- ID: `casehold_2345__semantic_noise__0`
- Role: `semantic_distractor`
- Source: `semantic_noise_from_casehold`
- Title: CaseHOLD legal context

As noted in the Advisory Committee notes to Rule 41(e) of the Federal Rules of Criminal Procedure, the district court has jurisdiction to hear motions “to compel [the] return of property obtained by an illegal search and seizure.” Fed. R.Crim.P. 41(e) advisory committee’s note. Moreover, the Third Circuit has found that its district courts have jurisdiction over third party motions for the return of property, see United States v. Frank, 763 F.2d 551, 552 (3d Cir.1985) (stating that the district court had jurisdiction to entertain a third party motion to determine who had entitlement to evidence after the criminal prosecution concluded), and that such jurisdiction exists even after the termination of the criminal proceedings, see United States v. McGlory, 202 F.3d 664, 670 (3d Cir.2000) (<HOLDING>); Bein, 214 F.3d at 411 (finding that “[a]

### Document 3

- ID: `casehold_2345__semantic_noise__1`
- Role: `semantic_distractor`
- Source: `semantic_noise_from_casehold`
- Title: CaseHOLD legal context

Commerce’s determination in the Final Results. (Pis.’ Br. on Jurisdiction 2-5.) In deciding between the appropriate bases for jurisdiction, the “ ‘mere recitation of a basis for jurisdiction, by either a party or a court, cannot be controllingt;]’ ” instead, the court “ ‘look[s] to the true nature of the action ... in determining jurisdiction.’ ” Norsk Hydro Can., Inc. v. United States, 472 F.3d 1347, 1355 (Fed.Cir.2006) (quoting Williams v. Sec’y of Navy, 787 F.2d 552, 557 (Fed.Cir.1986)). In this case, Plaintiffs challe t the time that the rule goes into effect because the relevant harm has already been inflicted: an interested party has lost the opportunity to alter the agency’s decision through full participation in the regulatory process. See, e.g., Wind River, 946 F.2d at 715 (<HOLDING>); Thrift Depositors of Am., Inc. v. Office of

### Document 4

- ID: `casehold_2345__semantic_noise__2`
- Role: `semantic_distractor`
- Source: `semantic_noise_from_casehold`
- Title: CaseHOLD legal context

was conscious of the confinement, (3) the plaintiff did not contest the confinement, and (4) the confinement was not otherwise privileged.” Broughton v. State, 37 N.Y.2d 451, 456, 373 N.Y.S.2d 87, 335 N.E.2d 310 (1975), cert. denied, 423 U.S. 929, 96 S.Ct. 277, 46 L.Ed.2d 257 (1975) (internal citations omitted). The only element in dispute in the instant case is the last element — defendant argues that the arrest was privileged as a matter of law because it was supported by probable cause. Fulton v. Robinson, 289 F.3d 188, 195 (2d. Cir.2002) (“A § 1983 claim of false arrest based on the Fourth Amendment right to be free from unreasonable seizures may not be maintained if there was probable cause for the arrest”); see also Bernard v. United States, 25 F.3d 98, 102 (2d Cir. 1994) (<HOLDING>); Cameron v. Fogarty, 806 F.2d 380, 387 (2d

### Document 5

- ID: `casehold_2345__semantic_noise__3`
- Role: `semantic_distractor`
- Source: `semantic_noise_from_casehold`
- Title: CaseHOLD legal context

was a convicted felon, and allow the State to parade the defendant’s prior felony history before the jury, over objection by the defendant, was an abuse of discretion and deprived defendant of his fundamental right to a fair trial. (A96) (emphasis added). Reviewing this sentence in the context of the arguments made in Petitioner’s Opening Brief, the Court likewise concludes that it is insufficient to put the state supreme court on notice that Petitioner was raising a federal constitutional claim. As the Court noted, Petitioner did not analyze his claim in constitutional terms and his reference to Old Chief as not binding on the state courts undermines Petitioner’s argument that he raised a federal constitutional claim. See e.g. Bright v. Snyder, 218 F.Supp.2d 573, 578-579 (D.Del.2002) (<HOLDING>). In addition, the Court finds further support

### Document 6

- ID: `casehold_2345__semantic_noise__4`
- Role: `semantic_distractor`
- Source: `semantic_noise_from_casehold`
- Title: CaseHOLD legal context

the federal rules, recognized that it was to be “guided by court decisions interpreting these rules.” Miscellaneous Changes to Trademark Trial and Appeal Board Rules, 63 Fed.Reg. at 48,084. The majority relies on TBMP § 523.04 which states that where a party “fails to file a motion to challenge the sufficiency of the response [to its discovery request], it may not thereafter be heard to complain about the sufficiency thereof.” It is far from clear whether this provision was designed to deal with the supplementation requirement, or whether it was limited to deal with the failure to provide initial responses. In any event, unlike the regulations, this section of the TBMP does not have the force and effect of law. See In re Pennington Seed, Inc., 466 F.3d 1053, 1059 (Fed.Cir.2006) (<HOLDING>). In the past, we have declined to follow

### Document 7

- ID: `casehold_2345__semantic_noise__5`
- Role: `semantic_distractor`
- Source: `semantic_noise_from_casehold`
- Title: CaseHOLD legal context

time in their reply brief). The BIA did not violate petitioners’ due process rights. It is undisputed that the BIA mailed its decision to petitioners’ attorney of record, that he received it, and that petitioners failed to inform the BIA of their change of address. Further, the record shows that the IJ told petitioners that they were required to inform the agency if they changed their address and that he gave them the change of address form. We lack jurisdiction to consider petitioners’ remaining contentions because they arise from the agency’s underlying decision to deny cancellation of removal. Petitioners failed to seek review of that decision within the 30-day time limit prescribed by 8 U.S.C. § 1252(b)(1). See Stone v. INS, 514 U.S. 386, 405, 115 S.Ct. 1537, 131 L.Ed.2d 465 (1995) (<HOLDING>). DENIED in part, DISMISSED in part. *** This

### Document 8

- ID: `casehold_2345__semantic_noise__6`
- Role: `semantic_distractor`
- Source: `semantic_noise_from_casehold`
- Title: CaseHOLD legal context

See also Matter of Schultz Mfg. Fabricating Co., 956 F.2d 686, 689 (7th Cir.1992) (finding no district court jurisdiction in the absence of a timely notice of appeal from the bankruptcy court). of appeal within 10 dismissing the peti- But the order refusing to convert the Chapter 7 proceedings from New York into the Chapter 13 proceedings in Illinois was not a final order. It did not bring the Illinois Chapter 13 petition to an end; virtually the entire dispute remained, involving the same parties and the same issues. Even though the concept of finality is relaxed in the bankruptcy context, see In re Jartran, Inc., 886 F.2d 859, 861-62 (7th Cir.1989), this order was interlocutory in the purest sense of the word. See Caldwell-Baker Co. v. Parsons, 392 F.3d 886, 888 (7th Cir.2004) (<HOLDING>). See also In re Young, 237 F.3d 1168, 1172-73

### Document 9

- ID: `casehold_2345__semantic_noise__7`
- Role: `semantic_distractor`
- Source: `semantic_noise_from_casehold`
- Title: CaseHOLD legal context

is to examine, in light of agistrate in issuing search warrant “is to make a practical, common sense decision whether, given all the circumstances set forth in the warrant’s supporting affidavit, including the veracity and basis of knowledge of persons supplying hearsay information, there is a fair probability that contraband or evidence of a crime will be found in a particular place”). However, when an affidavit in support of a search warrant based on information obtained from an informant fails to state when the affiant received the information from the informant, when the informant obtained his information, or when the incident described took place, the affidavit is inadequate to support the issuance of a search warrant. See Schmidt v. State, 659 S.W.2d 420, 421 (Tex.Crim.App.1983) (<HOLDING>). Here, Officer Brinson’s affidavit supporting

**Human judgment:** PASS / FAIL / UNCERTAIN

**Reason:**

---

## Case 05: casehold / partial

**Instance ID:** `casehold_3538__partial`

**Question:** Which holding is best supported by the retrieved legal context? Choose one option. Options: A) holding that in deciding on a facial constitutional challenge it is improper to consider only limited hypothetical applications B) recognizing that courts should exercise judicial restraint in a facial challenge C) holding that exhaustion of arbitration procedure is not necessary before the district court could consider a facial constitutional challenge D) holding that taxpayer was still required to go through tax refund procedure despite facial constitutional challenge to state intangibles tax E) holding a new constitutional challenge not raised in district court was not properly before court of appeals

**Gold answer:** holding that exhaustion of arbitration procedure is not necessary before the district court could consider a facial constitutional challenge

**Expected abstention:** True

**Retained ratio:** 0.6245572609208973

**Evidence:**

### Document 1

- ID: `casehold_3538__partial__casehold_3538_gold_0`
- Role: `partial_support`
- Source: `casehold_partial_v3`
- Title: CaseHOLD legal context | partial evidence

of the provision to his situation. Federal Trade Commission v. Standard Oil Co. of California, 449 U.S. [232], 239-245, 101 S.Ct. [488], 493-496, 66 L.Ed.2d 416. Id. at 488. § 1401. See Terson Company, Inc. v. Bakery Drivers and Salesmen Local 194, 739 F.2d 118, 121 (3d Cir.1984) (The basis of Terson’s as applied challenge is not apparent from the published decision.); Republic Industries, Inc. v. Central Pennsylvania Teamsters Pension Fund, 693 F.2d 290, 296 (3d Cir.1982) (<HOLDING>); See also, Republic Industries, Inc. v.

### Document 2

- ID: `casehold_3538__semantic_noise__0`
- Role: `semantic_distractor`
- Source: `semantic_noise_from_casehold`
- Title: CaseHOLD legal context

was a convicted felon, and allow the State to parade the defendant’s prior felony history before the jury, over objection by the defendant, was an abuse of discretion and deprived defendant of his fundamental right to a fair trial. (A96) (emphasis added). Reviewing this sentence in the context of the arguments made in Petitioner’s Opening Brief, the Court likewise concludes that it is insufficient to put the state supreme court on notice that Petitioner was raising a federal constitutional claim. As the Court noted, Petitioner did not analyze his claim in constitutional terms and his reference to Old Chief as not binding on the state courts undermines Petitioner’s argument that he raised a federal constitutional claim. See e.g. Bright v. Snyder, 218 F.Supp.2d 573, 578-579 (D.Del.2002) (<HOLDING>). In addition, the Court finds further support

### Document 3

- ID: `casehold_3538__semantic_noise__1`
- Role: `semantic_distractor`
- Source: `semantic_noise_from_casehold`
- Title: CaseHOLD legal context

the federal rules, recognized that it was to be “guided by court decisions interpreting these rules.” Miscellaneous Changes to Trademark Trial and Appeal Board Rules, 63 Fed.Reg. at 48,084. The majority relies on TBMP § 523.04 which states that where a party “fails to file a motion to challenge the sufficiency of the response [to its discovery request], it may not thereafter be heard to complain about the sufficiency thereof.” It is far from clear whether this provision was designed to deal with the supplementation requirement, or whether it was limited to deal with the failure to provide initial responses. In any event, unlike the regulations, this section of the TBMP does not have the force and effect of law. See In re Pennington Seed, Inc., 466 F.3d 1053, 1059 (Fed.Cir.2006) (<HOLDING>). In the past, we have declined to follow

**Human judgment:** PASS / FAIL / UNCERTAIN

**Reason:**

---

## Case 06: casehold / stale

**Instance ID:** `casehold_2537__stale`

**Question:** Which holding is best supported by the retrieved legal context? Choose one option. Options: A) holding that department of transportation did not have control of motorists drivers license because although the department of transportation may have had a duty to recall the motorists license this authority to revoke does not involve physical possession or actual control sufficient to bring the license within the ambit of the personal property exception to sovereign immunity B) holding that age disclosed on a drivers license constituted an admission where the party swore to the truth of the statements made in the license application C) holding that possession of a drivers license is irrelevant to the offense of failing to present a license which is completed by failing to present the license when requested to do so by an officer D) recognizing that the due process guaranteed under the alabama constitution is coextensive with the due process guaranteed under the united states constitution E) holding that the commonwealth cannot revoke a drivers license without due process required by the constitution

**Gold answer:** holding that the commonwealth cannot revoke a drivers license without due process required by the constitution

**Expected abstention:** True

**Evidence:**

### Document 1

- ID: `casehold_2537__stale_doc`
- Role: `stale`
- Source: `synthetic_controlled_stale_v3`
- Title: Archived source snapshot (2017)

Snapshot date: 2017-06-30. Question recorded: Which holding is best supported by the retrieved legal context? Choose one option. Options: A) holding that department of transportation did not have control of motorists drivers license because although the department of transportation may have had a duty to recall the motorists license this authority to revoke does not involve physical possession or actual control sufficient to bring the license within the ambit of the personal property exception to sovereign immunity B) holding that age disclosed on a drivers license constituted an admission where the party swore to the truth of the statements made in the license application C) holding that possession of a drivers license is irrelevant to the offense of failing to present a license which is completed by failing to present the license when requested to do so by an officer D) recognizing that the due process guaranteed under the alabama constitution is coextensive with the due process guaranteed under the united states constitution E) holding that the commonwealth cannot revoke a drivers license without due process required by the constitution Reported answer in this snapshot: holding  ...

### Document 2

- ID: `casehold_2537__semantic_noise__0`
- Role: `semantic_distractor`
- Source: `semantic_noise_from_casehold`
- Title: CaseHOLD legal context

was conscious of the confinement, (3) the plaintiff did not contest the confinement, and (4) the confinement was not otherwise privileged.” Broughton v. State, 37 N.Y.2d 451, 456, 373 N.Y.S.2d 87, 335 N.E.2d 310 (1975), cert. denied, 423 U.S. 929, 96 S.Ct. 277, 46 L.Ed.2d 257 (1975) (internal citations omitted). The only element in dispute in the instant case is the last element — defendant argues that the arrest was privileged as a matter of law because it was supported by probable cause. Fulton v. Robinson, 289 F.3d 188, 195 (2d. Cir.2002) (“A § 1983 claim of false arrest based on the Fourth Amendment right to be free from unreasonable seizures may not be maintained if there was probable cause for the arrest”); see also Bernard v. United States, 25 F.3d 98, 102 (2d Cir. 1994) (<HOLDING>); Cameron v. Fogarty, 806 F.2d 380, 387 (2d

### Document 3

- ID: `casehold_2537__semantic_noise__1`
- Role: `semantic_distractor`
- Source: `semantic_noise_from_casehold`
- Title: CaseHOLD legal context

... [and (2) ] immediately recognizes the object[ ] discovered as evidence of wrongdoing.’” ” State v. Otwell, 733 So.2d 950, 953 (Ala.Crim.App.1999) (quoting Smith v. State, 472 So.2d 677, 682-83 (Ala.Crim.App.1984), quoting in turn Herrin v. State, 349 So.2d 103 (Ala.Crim.App.1977)). See also Otwell, 733 So.2d at 953 (recognizing that there is no requirement under the plain-view doctrine that the officer come upon the evidence inadvertently). Here, there is no dispute that Cpl. Wells lawfully stopped Moore for running a stop sign. See Perry, 66 So.3d at 294 (explaining the law-enforcement officers may lawfully stop the driver of a vehicle for a traffic violation). Once Moore was lawfully stopped, Cpl. Wells properly ordered him to get out of the vehicle. See Mimms, 434 U.S. at 111 (<HOLDING>); Perry, 66 So.3d at 294 (same). After Moore

### Document 4

- ID: `casehold_2537__semantic_noise__2`
- Role: `semantic_distractor`
- Source: `semantic_noise_from_casehold`
- Title: CaseHOLD legal context

was a convicted felon, and allow the State to parade the defendant’s prior felony history before the jury, over objection by the defendant, was an abuse of discretion and deprived defendant of his fundamental right to a fair trial. (A96) (emphasis added). Reviewing this sentence in the context of the arguments made in Petitioner’s Opening Brief, the Court likewise concludes that it is insufficient to put the state supreme court on notice that Petitioner was raising a federal constitutional claim. As the Court noted, Petitioner did not analyze his claim in constitutional terms and his reference to Old Chief as not binding on the state courts undermines Petitioner’s argument that he raised a federal constitutional claim. See e.g. Bright v. Snyder, 218 F.Supp.2d 573, 578-579 (D.Del.2002) (<HOLDING>). In addition, the Court finds further support

### Document 5

- ID: `casehold_2537__semantic_noise__3`
- Role: `semantic_distractor`
- Source: `semantic_noise_from_casehold`
- Title: CaseHOLD legal context

officer must be able to point to specific and articulable facts which, taken together with rational inferences from those facts, reasonably warrant a finding that a breach of the peace is imminent or the public safety is threatened.” Ecker, 311 So.2d at 109 (quoting Terry v. Ohio, 392 U.S. 1, 21, 88 S.Ct. 1868, 1880, 20 L.Ed.2d 889, 906 (1968)). See also Williams v. State, 674 So.2d 885 (Fla. 2d DCA 1996). “Moreover, failure to provide identification is not an element of the charged offense. While the statute gives the suspect an opportunity to explain his presence and conduct, the criminal conduct must be completed prior to any action by police officers.” E.B. v. State, 537 So.2d 148 (Fla. 2d DCA 1989) (citations omitted). See also R.D.W. v. State, 659 So.2d 1193 (Fla. 2d DCA 1995)(<HOLDING>). In the present case, assuming that sitting

### Document 6

- ID: `casehold_2537__semantic_noise__4`
- Role: `semantic_distractor`
- Source: `semantic_noise_from_casehold`
- Title: CaseHOLD legal context

the district court’s denial of its motion to dismiss on grounds of Alamo’s Eleventh Amendment immunity. Martin argues that we are precluded from considering the merits of this issue because Alamo did not file a timely notice of appeal. We need not decide whether Alamo’s notice of appeal was timely because Alamo inadequately briefed the issue and, thus, abandoned its Eleventh Amendment arguments. Southwestern Bell Tel. Co. v. City of El Paso, 243 F.3d 936, 940 (5th Cir.2001) (dismissing appeal as abandoned because the Appellant failed to challenge the district court’s application of the applicable test for Eleventh Amendment immunity); Dardar v. Lafourche Realty Co., 985 F.2d 824, 831 (5th Cir.0993); L & A Contracting Co. v. Southern Concrete Servs., 17 F.3d 106, 113 (5th Cir.1994)(<HOLDING>); Fed. R.App. P. 28(a)(9)(A) (requiring

### Document 7

- ID: `casehold_2537__semantic_noise__5`
- Role: `semantic_distractor`
- Source: `semantic_noise_from_casehold`
- Title: CaseHOLD legal context

claim or might motivate the court of appeals to raise such a claim on its own. In summary, under the circumstances, the court of appeals ought to have addressed the preservation issue urged in the State’s motion for rehearing. This case involves a serious question about whether error was in fact preserved under common, everyday notions of procedural default. This Court should either remand the case to the court of appeals to consider the issue or it should consider the preservation issue on discretionary review. I respectfully dissent to the Court’s decision to dismiss this petition as improvidently granted. 1 . 791 S.W.2d 121 (Tex.Crim.App.1990). 2 . Jones v. State, 942 S.W.2d 1, 2 n. 1 (Tex.Crim.App.1997); see also Hughes v. State, 878 S.W.2d 142, 151 (Tex.Crim.App.1992) (<HOLDING>) and Fuller v. State, 829 S.W.2d 191, 199 n. 4

### Document 8

- ID: `casehold_2537__semantic_noise__6`
- Role: `semantic_distractor`
- Source: `semantic_noise_from_casehold`
- Title: CaseHOLD legal context

Opinion at 4-5. His fears are unfounded. First, the state action requirement, operating entirely apart from the standing requirement, would obviously screen out the vast majority of consumer-preference grievances, for a consumer aggrieved about the disappearance of his favorite brand would have to find a cause of action against a governmental body or face dismissal for failure to state a claim. In any event, of those claims that remain, the independent causation requirement of the standing requirement would bar the tenuous claims Judge Silberman fears from ever reaching the merits. Only those consumers who could prove that a "substantial likelihood,” see Duke Power Co., 438 U.S. at 75 n. 20, 98 S.Ct. at 2631 n. 20, existed that the governmental 2232, 2241, 65 L.Ed.2d 184 (1980) (<HOLDING>); see also Autolog Corp. v. Regan, 731 F.2d 25,

### Document 9

- ID: `casehold_2537__semantic_noise__7`
- Role: `semantic_distractor`
- Source: `semantic_noise_from_casehold`
- Title: CaseHOLD legal context

applied the relevant substantive law. Id. The grant of summary judgment in this case is reviewed in light of the quite summary procedural requirements provided by the statutory law of civil forfeitures. United States v. One 56-Foot Motor Yacht Named the Tahuna, 702 F.2d 1276, 1281 (9th Cir.1983). 3 . Ordinarily, collateral estoppel is an affirmative defense that must be raised by the party seeking to use it, or else it is waived. See, e.g., Kern Oil & Ref. Co. v. Tenneco Oil Co., 840 F.2d 730, 735 (9th Cir.), cert. denied, 488 U.S. 948, 109 S.Ct. 378, 102 L.Ed.2d 367 (1988). The government did not brief the issue in this case; however, we raise it sua sponte in order to affirm the district court’s decision. See Russell v. SunAmerica Sec., Inc., 962 F.2d 1169, 1172 (5th Cir.1992) (<HOLDING>). 4 . The preclusive effect of a state court

**Human judgment:** PASS / FAIL / UNCERTAIN

**Reason:**

---

## Case 07: cuad / clean

**Instance ID:** `cuad_1986__clean`

**Question:** What text in this contract answers the clause category 'Insurance'?

**Gold answer:** MMT and SIGA shall each, at their sole cost and expense, procure and maintain (a) commercial general liability insurance in amounts not less than $[***] per incident and $[***] annual aggregate, and (c) product liability insurance in amounts not less than $[***] annual aggregate, and each naming the other Party as additional insured.

**Expected abstention:** False

**Evidence:**

### Document 1

- ID: `cuad_1986_gold_0`
- Role: `support`
- Source: `cuad`
- Title: SigaTechnologiesInc_20190603_8-K_EX-10.1_11695818_EX-10.1_Promotion Agreement.pdf | Insurance

MMT and SIGA shall each, at their sole cost and expense, procure and maintain (a) commercial general liability insurance in amounts not less than $[***] per incident and $[***] annual aggregate, and (c) product liability insurance in amounts not less than $[***] annual aggregate, and each naming the other Party as additional insured.

**Human judgment:** PASS / FAIL / UNCERTAIN

**Reason:**

---

## Case 08: cuad / contradictory

**Instance ID:** `cuad_11879__contradictory`

**Question:** What text in this contract answers the clause category 'Minimum Commitment'?

**Gold answer:** Dexcel shall supply the Product with at least **** percent (****%) of the shelf life upon Delivery unless otherwise agreed by the Parties.

**Expected abstention:** True

**Evidence:**

### Document 1

- ID: `cuad_11879_gold_0`
- Role: `support`
- Source: `cuad`
- Title: KitovPharmaLtd_20190326_20-F_EX-4.15_11584449_EX-4.15_Manufacturing Agreement.pdf | Minimum Commitment

Dexcel shall supply the Product with at least **** percent (****%) of the shelf life upon Delivery unless otherwise agreed by the Parties.

### Document 2

- ID: `cuad_11879__contradictory_doc`
- Role: `contradictory`
- Source: `synthetic_controlled_contradiction_v3`
- Title: Independent retrieved record

Question recorded: What text in this contract answers the clause category 'Minimum Commitment'? Reported answer: If requested by a Joint Venturer, the Joint Venture books and records shall be audited as of the close of each year by an independent accountant acceptable to both Joint Venturers.

### Document 3

- ID: `cuad_11879__semantic_noise__0`
- Role: `semantic_distractor`
- Source: `semantic_noise_from_cuad`
- Title: IntegrityMediaInc_20010329_10-K405_EX-10.17_2373875_EX-10.17_Co-Branding Agreement.pdf | Minimum Commitment

TL's initial order for each recorded Product shall be a minimum of five thousand (5,000) units.

### Document 4

- ID: `cuad_11879__semantic_noise__1`
- Role: `semantic_distractor`
- Source: `semantic_noise_from_cuad`
- Title: MPLXLP_06_17_2015-EX-10.1-TRANSPORTATION SERVICES AGREEMENT.pdf | Minimum Commitment

Shipper guarantees that during each Contract Year, Shipper will meet its Quarterly Volume Commitment or, in the event it fails to do so, shall remit to MPL the Quarterly Deficiency Payment pursuant to Section 3.5.

**Human judgment:** PASS / FAIL / UNCERTAIN

**Reason:**

---

## Case 09: cuad / missing

**Instance ID:** `cuad_12919__missing`

**Question:** What text in this contract answers the clause category 'Revenue/Profit Sharing'?

**Gold answer:** In consideration for providing these Services, AVDU shall pay UTK $120,000 worth of unregistered shares of common stock (31,413 shares) upon the execution of this Strategic Alliance Agreement.

**Expected abstention:** True

**Evidence:**

### Document 1

- ID: `cuad_12919__semantic_noise__0`
- Role: `semantic_distractor`
- Source: `semantic_noise_from_cuad`
- Title: LegacyEducationAllianceInc_20200330_10-K_EX-10.18_12090678_EX-10.18_Development Agreement.pdf | Revenue/Profit Sharing

For monthly Cash Sales above [$*] and up to [$*] , the Base Royalty paid to T&B by LEA shall be [*%]of the LEA's Cash Sales

### Document 2

- ID: `cuad_12919__semantic_noise__1`
- Role: `semantic_distractor`
- Source: `semantic_noise_from_cuad`
- Title: SoupmanInc_20150814_8-K_EX-10.1_9230148_EX-10.1_Franchise Agreement1.pdf | Revenue/Profit Sharing

Once you have units open and operating in the trade area where a National Account is located, we will remit to you 25% of the profits derived from the sales in that specific trade area.

### Document 3

- ID: `cuad_12919__semantic_noise__2`
- Role: `semantic_distractor`
- Source: `semantic_noise_from_cuad`
- Title: JOINTCORP_09_19_2014-EX-10.15-FRANCHISE AGREEMENT.pdf | Revenue/Profit Sharing

As of the date of this Agreement, the current required contribution to the Ad Fund is one percent (1%) of the gross revenues of the Franchise.

### Document 4

- ID: `cuad_12919__semantic_noise__3`
- Role: `semantic_distractor`
- Source: `semantic_noise_from_cuad`
- Title: RemarkHoldingsInc_20081114_10-Q_EX-10.24_2895649_EX-10.24_Content License Agreement.pdf | Cap On Liability

EXCEPT FOR EITHER PARTY'S VIOLATION OF THE CONFIDENTIALITY OBLIGATIONS AND FOR EITHER PARTY'S INDEMNIFICATION OBLIGATIONS, IN NO EVENT WILL EITHER PARTY BE LIABLE FOR SPECIAL, INCIDENTAL, CONSEQUENTIAL, INDIRECT OR PUNITIVE DAMAGES, OR LOST PROFITS, REGARDLESS OF WHETHER SUCH LIABILITY IS BASED ON BREACH OF CONTRACT, TORT, STRICT LIABILITY, BREACH OF WARRANTIES, FAILURE OF ESSENTIAL PURPOSE OR OTHERWISE AND EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGES.

### Document 5

- ID: `cuad_12919__semantic_noise__4`
- Role: `semantic_distractor`
- Source: `semantic_noise_from_cuad`
- Title: SouthernStarEnergyInc_20051202_SB-2A_EX-9_801890_EX-9_Affiliate Agreement.pdf | Revenue/Profit Sharing

The Advertising Cost Compensation depends on the actual sales generated by end users referred via the electronic advertisement (the Affiliate's link).

### Document 6

- ID: `cuad_12919__semantic_noise__5`
- Role: `semantic_distractor`
- Source: `semantic_noise_from_cuad`
- Title: RemarkHoldingsInc_20081114_10-Q_EX-10.24_2895649_EX-10.24_Content License Agreement.pdf | Anti-Assignment

Except as set forth herein, the parties shall not have any right or ability to assign, transfer, or sublicense any obligations or benefit under this Agreement without the prior written consent of the other party, which shall not be unreasonably withheld, except that, upon written notice to the other party, a party (i) may assign and transfer this Agreement and its rights and obligations hereunder to any third party who succeeds to substantially all its business, stock, or assets related to this Agreement, including, without limitation, to a Competitor (as defined below) (an "Acquisition"); and (ii) may assign or transfer any rights to receive payments hereunder.

### Document 7

- ID: `cuad_12919__semantic_noise__6`
- Role: `semantic_distractor`
- Source: `semantic_noise_from_cuad`
- Title: BERKELEYLIGHTS,INC_06_26_2020-EX-10.12-COLLABORATION AGREEMENT.pdf | Revenue/Profit Sharing

In the event that Ginkgo uses any of the BLI Proprietary Workflows identified in Exhibit D to conduct Commercial Services for a Third Party customer and such Commercial Services [***] result in the discovery of an Antibody to be used as the active ingredient in a therapeutic product for which a Third Party [***] (each such Antibody subject to this Section 7.4.2 (Milestone Payments), a "Discovered Antibody"), then, on a Discovered Antibody-by-Discovered Antibody basis, in the event such Third Party (a) achieves any of the milestone events noted below in Table 7.4.2 (each, a "Milestone Event") with respect to a Discovered Antibody and (b) makes a payment to Ginkgo in connection with such Milestone Event, then Ginkgo will pay BLI [***] percent ([***]%) of such payment received by Ginkgo from such Third Party up to the amount of the corresponding "Maximum Milestone Payment" for such milestone event set forth below in Table 7.4.2 (each, a "Milestone Payment".

### Document 8

- ID: `cuad_12919__semantic_noise__7`
- Role: `semantic_distractor`
- Source: `semantic_noise_from_cuad`
- Title: TURNKEYCAPITAL,INC_07_20_2017-EX-1.1-Strategic Alliance Agreement.pdf | Revenue/Profit Sharing

Net revenue from business operations created by Holding Company for the alliance will be distributed by Holding Company equally - 50/50 - to TKCI and SIC: SIC's original business concepts and plans, as well as opportunities brought to the table through its connections, and third-party contracts, are ways that we anticipate business could be generated, and revenues created; TKCI's advisory and management services and capital resources will provide the critical structure and business mechanism to carry concepts through to revenue.

**Human judgment:** PASS / FAIL / UNCERTAIN

**Reason:**

---

## Case 10: cuad / noisy

**Instance ID:** `cuad_8314__noisy`

**Question:** What text in this contract answers the clause category 'Cap On Liability'?

**Gold answer:** Notwithstanding anything contained in this Agreement to the contrary, neither Party shall be liable to the other Party for any special, consequential, incidental or punitive damages, however caused, based on any theory of liability except to the extent such damages are payable by such Party (a) pursuant to its indemnification obligations under Section 3.15 and infringement indemnification obligations under Section 3.17, (b) arising out of or resulting from such Party's breach of its confidentiality obligations set forth in this Agreement (including Section 3.16, Section 3.48, Section 4.2 and Exhibit A attached hereto) or (c) in connection with a Third Party Loss arising out of or resulting from such Party's violation of applicable Law.

**Expected abstention:** False

**Evidence:**

### Document 1

- ID: `cuad_8314_gold_0`
- Role: `support`
- Source: `cuad`
- Title: AtnInternationalInc_20191108_10-Q_EX-10.1_11878541_EX-10.1_Maintenance Agreement.pdf | Cap On Liability

Notwithstanding anything contained in this Agreement to the contrary, neither Party shall be liable to the other Party for any special, consequential, incidental or punitive damages, however caused, based on any theory of liability except to the extent such damages are payable by such Party (a) pursuant to its indemnification obligations under Section 3.15 and infringement indemnification obligations under Section 3.17, (b) arising out of or resulting from such Party's breach of its confidentiality obligations set forth in this Agreement (including Section 3.16, Section 3.48, Section 4.2 and Exhibit A attached hereto) or (c) in connection with a Third Party Loss arising out of or resulting from such Party's violation of applicable Law.

### Document 2

- ID: `cuad_8314__semantic_noise__0`
- Role: `semantic_distractor`
- Source: `semantic_noise_from_cuad`
- Title: IbioInc_20200313_8-K_EX-10.1_12052678_EX-10.1_Development Agreement.pdf | Cap On Liability

Except for claims arising out of Articles 4.3 and 7.0, or as may be set forth in a SOW, neither Party will be liable for any consequential damages, lost profits, lost savings, loss of anticipated revenue, or any exemplary, punitive, special or indirect damages, even if advised of their possibility.

### Document 3

- ID: `cuad_8314__semantic_noise__1`
- Role: `semantic_distractor`
- Source: `semantic_noise_from_cuad`
- Title: RemarkHoldingsInc_20081114_10-Q_EX-10.24_2895649_EX-10.24_Content License Agreement.pdf | Cap On Liability

EXCEPT FOR EITHER PARTY'S VIOLATION OF THE CONFIDENTIALITY OBLIGATIONS AND FOR EITHER PARTY'S INDEMNIFICATION OBLIGATIONS, IN NO EVENT WILL EITHER PARTY BE LIABLE FOR SPECIAL, INCIDENTAL, CONSEQUENTIAL, INDIRECT OR PUNITIVE DAMAGES, OR LOST PROFITS, REGARDLESS OF WHETHER SUCH LIABILITY IS BASED ON BREACH OF CONTRACT, TORT, STRICT LIABILITY, BREACH OF WARRANTIES, FAILURE OF ESSENTIAL PURPOSE OR OTHERWISE AND EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGES.

### Document 4

- ID: `cuad_8314__semantic_noise__2`
- Role: `semantic_distractor`
- Source: `semantic_noise_from_cuad`
- Title: AFSALABANCORPINC_08_01_1996-EX-1.1-AGENCY AGREEMENT.pdf | Cap On Liability

It is expressly agreed that Capital Resources shall not be liable for any loss, liability, claim, damage or expense or be required to contribute any amount which in the aggregate exceeds the amount paid (excluding reimbursable expenses) to Capital Resources under this Agreement.

### Document 5

- ID: `cuad_8314__semantic_noise__3`
- Role: `semantic_distractor`
- Source: `semantic_noise_from_cuad`
- Title: SEASPINEHOLDINGSCORP_10_10_2018-EX-10.1-SUPPLY AGREEMENT.pdf | Cap On Liability

NEITHER PARTY SHALL BE LIABLE TO THE OTHER FOR ANY SPECIAL, CONSEQUENTIAL, INCIDENTAL, OR INDIRECT DAMAGES ARISING FROM OR RELATING TO ANY BREACH OF THIS AGREEMENT, REGARDLESS OF ANY NOTICE OF THE POSSIBILITY OF SUCH DAMAGES.

### Document 6

- ID: `cuad_8314__semantic_noise__4`
- Role: `semantic_distractor`
- Source: `semantic_noise_from_cuad`
- Title: BloomEnergyCorp_20180321_DRSA (on S-1)_EX-10_11240356_EX-10_Maintenance Agreement.pdf | Uncapped Liability

provided that such limitation of liability shall not apply to any liability that is the result of (i) gross negligence, fraud or willful misconduct of a Party, (ii) a Third Party Claim, (iii) the failure to pay the Service Fees (which amount shall not be included in calculating Owner's Maximum Liability), (iv) a claim of Owner against BE or Operator in the event of any breach, default or misrepresentation of any representation and warranty or covenant set forth in Section 8.2(e) or (v) a claim of Owner against BE or Operator under Section 2.8.

### Document 7

- ID: `cuad_8314__semantic_noise__5`
- Role: `semantic_distractor`
- Source: `semantic_noise_from_cuad`
- Title: BNLFINANCIALCORP_03_30_2007-EX-10.8-OUTSOURCING AGREEMENT.pdf | Cap On Liability

Any claim of action of any kind which one party to this Agreement may have against the other party relating to or arising out of this Agreement must be commenced within two (2) years from the date such claim or cause of action shall have first accrued.

### Document 8

- ID: `cuad_8314__semantic_noise__6`
- Role: `semantic_distractor`
- Source: `semantic_noise_from_cuad`
- Title: HealthcentralCom_19991108_S-1A_EX-10.27_6623292_EX-10.27_Co-Branding Agreement.pdf | Uncapped Liability

EXCEPT WITH RESPECT TO THE INDEMNITY OBLIGATIONS IN SECTION 14, THE CONFIDENTIALITY OBLIGATIONS UNDER SECTION 16, AND THE YEAR 2000 COMPLIANCE OBLIGATIONS UNDER SECTION 20, NOTWITHSTANDING ANYTHING TO THE CONTRARY CONTAINED IN THIS AGREEMENT, UNDER NO CIRCUMSTANCES SHALL EITHER PARTY BE LIABLE TO THE OTHER PARTY WITH RESPECT TO THE SUBJECT MATTER OF THIS AGREEMENT UNDER ANY CONTRACT, NEGLIGENCE, 10 STRICT LIABILITY, TORT OR OTHER LEGAL OR EQUITABLE THEORY FOR ANY INDIRECT, INCIDENTAL, CONSEQUENTIAL, SPECIAL OR EXEMPLARY DAMAGES (INCLUDING, WITHOUT LIMITATION, LOSS OF REVENUE OR GOODWILL OR ANTICIPATED PROFITS OR LOST BUSINESS), EVEN IF SUCH PARTY HAS BEEN ADVISED OF THE POSSIBILITY OF SUCH DAMAGES.

### Document 9

- ID: `cuad_8314__semantic_noise__7`
- Role: `semantic_distractor`
- Source: `semantic_noise_from_cuad`
- Title: MorganStanleyDirectLendingFund_20191119_10-12GA_EX-10.5_11898508_EX-10.5_Trademark License Agreement.pdf | Cap On Liability

EXCEPT WITH RESPECT TO LICENSEE'S INDEMNIFICATION OBLIGATIONS UNDER SECTION 7, NEITHER PARTY WILL BE LIABLE TO THE OTHER PARTY FOR SPECIAL, INDIRECT, CONSEQUENTIAL, EXEMPLARY, PUNITIVE OR INCIDENTAL DAMAGES (INCLUDING LOST PROFITS OR GOODWILL, BUSINESS <omitted> INTERRUPTION AND THE LIKE) RELATING TO THIS AGREEMENT, EVEN IF IT HAS BEEN ADVISED OF THE POSSIBILITY OF SUCH DAMAGES.

**Human judgment:** PASS / FAIL / UNCERTAIN

**Reason:**

---

## Case 11: cuad / partial

**Instance ID:** `cuad_11213__partial`

**Question:** What text in this contract answers the clause category 'Price Restrictions'?

**Gold answer:** The prices payable by Ultragenyx to Cremer for the Product (the "Price") shall be agreed [***] every contract year; provided, that the Price may not increase more than the [***] for such period or [***]%, whichever is higher.

**Expected abstention:** True

**Retained ratio:** 0.3466666666666667

**Evidence:**

### Document 1

- ID: `cuad_11213__partial__cuad_11213_gold_0`
- Role: `partial_support`
- Source: `cuad_partial_v3`
- Title: ULTRAGENYXPHARMACEUTICALINC_12_23_2013-EX-10.9-SUPPLY AGREEMENT.pdf | Price Restrictions | partial evidence

The prices payable by Ultragenyx to Cremer for the Product (the "Price") shall

### Document 2

- ID: `cuad_11213__semantic_noise__0`
- Role: `semantic_distractor`
- Source: `semantic_noise_from_cuad`
- Title: EhaveInc_20190515_20-F_EX-4.44_11678816_EX-4.44_License Agreement_ Reseller Agreement.pdf | Competitive Restriction Exception

For clarity, a Competitive Transaction shall not include an agreement for use, integration or interfacing, or co-marketing, of the Ehave Companion Solution with other services, solutions, devices, goods or products, where such other services, solutions, devices, goods or products do not contain the same or similar functionality of the Ehave Companion Solution, but provides for a complementary solution.

### Document 3

- ID: `cuad_11213__semantic_noise__1`
- Role: `semantic_distractor`
- Source: `semantic_noise_from_cuad`
- Title: RemarkHoldingsInc_20081114_10-Q_EX-10.24_2895649_EX-10.24_Content License Agreement.pdf | Anti-Assignment

Except as set forth herein, the parties shall not have any right or ability to assign, transfer, or sublicense any obligations or benefit under this Agreement without the prior written consent of the other party, which shall not be unreasonably withheld, except that, upon written notice to the other party, a party (i) may assign and transfer this Agreement and its rights and obligations hereunder to any third party who succeeds to substantially all its business, stock, or assets related to this Agreement, including, without limitation, to a Competitor (as defined below) (an "Acquisition"); and (ii) may assign or transfer any rights to receive payments hereunder.

**Human judgment:** PASS / FAIL / UNCERTAIN

**Reason:**

---

## Case 12: cuad / stale

**Instance ID:** `cuad_12833__stale`

**Question:** What text in this contract answers the clause category 'Revenue/Profit Sharing'?

**Gold answer:** Notwithstanding anything herein to the contrary, WYZZ shall continue to be the owner of and shall be entitled to all revenues resulting from the sale of advertising and other time on WYZZ-TV before, during and/or after the Term; provided, however, in consideration of the Services, Nexstar shall be entitled to all revenues resulting from the sale of advertising and other time on the Stations during the Term remaining after the payment of the amounts set forth below: (a) Within seventy-five (75) days following the end of each month of a calendar year during the Term that "BCF" (as defined below) for such month, when combined with BCF for all prior months during such calendar year (other than any month which is outside the Term) is less than the Minimum BCF, Nexstar shall pay a fee to WYZZ in an amount equal to thirty-five percent (35%) of BCF for such month. Within seventy-five (75) days following the end of each month of a calendar year during the Term that BCF for such month, when combined with BCF for all prior months of such calendar year (other than any month which is outside the Term) is greater than the Minimum BCF, Nexstar shall pay a fee to WYZZ in an amount equal to 50% of

**Expected abstention:** True

**Evidence:**

### Document 1

- ID: `cuad_12833__stale_doc`
- Role: `stale`
- Source: `synthetic_controlled_stale_v3`
- Title: Archived source snapshot (2017)

Snapshot date: 2017-06-30. Question recorded: What text in this contract answers the clause category 'Revenue/Profit Sharing'? Reported answer in this snapshot: The Parties agree that notwithstanding any termination or expiration of this Agreement, the rights and licenses granted to any Company- Skype Branded Customers prior to termination or expiration of this Agreement pursuant to any EULA shall continue during the 24 months after such termination or expiration for the sole purpose of permitting such users to continue to access and utilize the Company-Skype Branded Application and the Company-Skype Toolbar, and so long as any Gross Revenue is

### Document 2

- ID: `cuad_12833__semantic_noise__0`
- Role: `semantic_distractor`
- Source: `semantic_noise_from_cuad`
- Title: LegacyEducationAllianceInc_20200330_10-K_EX-10.18_12090678_EX-10.18_Development Agreement.pdf | Revenue/Profit Sharing

For monthly Cash Sales above [$*] and up to [$*] , the Base Royalty paid to T&B by LEA shall be [*%]of the LEA's Cash Sales

### Document 3

- ID: `cuad_12833__semantic_noise__1`
- Role: `semantic_distractor`
- Source: `semantic_noise_from_cuad`
- Title: SoupmanInc_20150814_8-K_EX-10.1_9230148_EX-10.1_Franchise Agreement1.pdf | Revenue/Profit Sharing

Once you have units open and operating in the trade area where a National Account is located, we will remit to you 25% of the profits derived from the sales in that specific trade area.

### Document 4

- ID: `cuad_12833__semantic_noise__2`
- Role: `semantic_distractor`
- Source: `semantic_noise_from_cuad`
- Title: JOINTCORP_09_19_2014-EX-10.15-FRANCHISE AGREEMENT.pdf | Revenue/Profit Sharing

As of the date of this Agreement, the current required contribution to the Ad Fund is one percent (1%) of the gross revenues of the Franchise.

### Document 5

- ID: `cuad_12833__semantic_noise__3`
- Role: `semantic_distractor`
- Source: `semantic_noise_from_cuad`
- Title: RemarkHoldingsInc_20081114_10-Q_EX-10.24_2895649_EX-10.24_Content License Agreement.pdf | Cap On Liability

EXCEPT FOR EITHER PARTY'S VIOLATION OF THE CONFIDENTIALITY OBLIGATIONS AND FOR EITHER PARTY'S INDEMNIFICATION OBLIGATIONS, IN NO EVENT WILL EITHER PARTY BE LIABLE FOR SPECIAL, INCIDENTAL, CONSEQUENTIAL, INDIRECT OR PUNITIVE DAMAGES, OR LOST PROFITS, REGARDLESS OF WHETHER SUCH LIABILITY IS BASED ON BREACH OF CONTRACT, TORT, STRICT LIABILITY, BREACH OF WARRANTIES, FAILURE OF ESSENTIAL PURPOSE OR OTHERWISE AND EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGES.

### Document 6

- ID: `cuad_12833__semantic_noise__4`
- Role: `semantic_distractor`
- Source: `semantic_noise_from_cuad`
- Title: SouthernStarEnergyInc_20051202_SB-2A_EX-9_801890_EX-9_Affiliate Agreement.pdf | Revenue/Profit Sharing

The Advertising Cost Compensation depends on the actual sales generated by end users referred via the electronic advertisement (the Affiliate's link).

### Document 7

- ID: `cuad_12833__semantic_noise__5`
- Role: `semantic_distractor`
- Source: `semantic_noise_from_cuad`
- Title: RemarkHoldingsInc_20081114_10-Q_EX-10.24_2895649_EX-10.24_Content License Agreement.pdf | Anti-Assignment

Except as set forth herein, the parties shall not have any right or ability to assign, transfer, or sublicense any obligations or benefit under this Agreement without the prior written consent of the other party, which shall not be unreasonably withheld, except that, upon written notice to the other party, a party (i) may assign and transfer this Agreement and its rights and obligations hereunder to any third party who succeeds to substantially all its business, stock, or assets related to this Agreement, including, without limitation, to a Competitor (as defined below) (an "Acquisition"); and (ii) may assign or transfer any rights to receive payments hereunder.

### Document 8

- ID: `cuad_12833__semantic_noise__6`
- Role: `semantic_distractor`
- Source: `semantic_noise_from_cuad`
- Title: BERKELEYLIGHTS,INC_06_26_2020-EX-10.12-COLLABORATION AGREEMENT.pdf | Revenue/Profit Sharing

In the event that Ginkgo uses any of the BLI Proprietary Workflows identified in Exhibit D to conduct Commercial Services for a Third Party customer and such Commercial Services [***] result in the discovery of an Antibody to be used as the active ingredient in a therapeutic product for which a Third Party [***] (each such Antibody subject to this Section 7.4.2 (Milestone Payments), a "Discovered Antibody"), then, on a Discovered Antibody-by-Discovered Antibody basis, in the event such Third Party (a) achieves any of the milestone events noted below in Table 7.4.2 (each, a "Milestone Event") with respect to a Discovered Antibody and (b) makes a payment to Ginkgo in connection with such Milestone Event, then Ginkgo will pay BLI [***] percent ([***]%) of such payment received by Ginkgo from such Third Party up to the amount of the corresponding "Maximum Milestone Payment" for such milestone event set forth below in Table 7.4.2 (each, a "Milestone Payment".

### Document 9

- ID: `cuad_12833__semantic_noise__7`
- Role: `semantic_distractor`
- Source: `semantic_noise_from_cuad`
- Title: BORROWMONEYCOM,INC_06_11_2020-EX-10.1-JOINT VENTURE AGREEMENT.pdf | Parties

(individually the "Member" and collectively the "Members"

**Human judgment:** PASS / FAIL / UNCERTAIN

**Reason:**

---

## Case 13: fever / clean

**Instance ID:** `fever_33604__clean`

**Question:** Verify this claim: Birmingham is in the West Midlands.

**Gold answer:** SUPPORTS

**Expected abstention:** False

**Evidence:**

### Document 1

- ID: `fever_33604_gold_0`
- Role: `support`
- Source: `fever`
- Title: FEVER evidence for claim 33604

Birmingham sentence 0: Birmingham -LRB- -LSB- ˈbɜːmɪŋəm -RSB- -RRB- is a city and metropolitan borough in the West Midlands , England .

**Human judgment:** PASS / FAIL / UNCERTAIN

**Reason:**

---

## Case 14: fever / contradictory

**Instance ID:** `fever_37229__contradictory`

**Question:** Verify this claim: Life is separate from physical entities.

**Gold answer:** REFUTES

**Expected abstention:** True

**Evidence:**

### Document 1

- ID: `fever_37229_gold_0`
- Role: `support`
- Source: `fever`
- Title: FEVER evidence for claim 37229

Life sentence 0: Life is a characteristic distinguishing physical entities having biological processes , such as signaling and self-sustaining processes , from those that do not , either because such functions have ceased , or because they never had such functions and are classified as inanimate .

### Document 2

- ID: `fever_37229__contradictory_doc`
- Role: `contradictory`
- Source: `synthetic_controlled_contradiction_v3`
- Title: Independent retrieved record

Question recorded: Verify this claim: Life is separate from physical entities. Reported answer: supports

### Document 3

- ID: `fever_37229__semantic_noise__0`
- Role: `semantic_distractor`
- Source: `semantic_noise_from_fever`
- Title: FEVER evidence for claim 228432

The_Wallace_-LRB-poem-RRB- sentence 2: The poem is historically inaccurate , and mentions several events that never happened .

### Document 4

- ID: `fever_37229__semantic_noise__1`
- Role: `semantic_distractor`
- Source: `semantic_noise_from_fever`
- Title: FEVER evidence for claim 156076

Kleshas_-LRB-Buddhism-RRB- sentence 0: Kleshas -LRB- -LSB- क्लेश , kleśa -RSB- किलेस kilesa ; ཉ ན མ ངས nyon mongs -RRB- , in Buddhism , are mental states that cloud the mind and manifest in unwholesome actions .

**Human judgment:** PASS / FAIL / UNCERTAIN

**Reason:**

---

## Case 15: fever / missing

**Instance ID:** `fever_99435__missing`

**Question:** Verify this claim: Color of Night is still in production.

**Gold answer:** REFUTES

**Expected abstention:** True

**Evidence:**

### Document 1

- ID: `fever_99435__semantic_noise__0`
- Role: `semantic_distractor`
- Source: `semantic_noise_from_fever`
- Title: FEVER evidence for claim 113422

Night_of_the_Living_Dead sentence 0: Night of the Living Dead is a 1968 American independent horror film , directed by George A. Romero , starring Duane Jones and Judith O'Dea .

### Document 2

- ID: `fever_99435__semantic_noise__1`
- Role: `semantic_distractor`
- Source: `semantic_noise_from_fever`
- Title: FEVER evidence for claim 179105

The_Good_German sentence 1: It was directed by Steven Soderbergh , and stars George Clooney , Cate Blanchett , and Tobey Maguire .

### Document 3

- ID: `fever_99435__semantic_noise__2`
- Role: `semantic_distractor`
- Source: `semantic_noise_from_fever`
- Title: FEVER evidence for claim 33222

The_Incredibles_2 sentence 3: The movie is scheduled to be released on June 15 , 2018 and will be given an IMAX release .

### Document 4

- ID: `fever_99435__semantic_noise__3`
- Role: `semantic_distractor`
- Source: `semantic_noise_from_fever`
- Title: FEVER evidence for claim 148541

The_Quiet sentence 4: The film was acquired by Destination Films , which released this film in the United States theatrically through Sony Pictures Classics on August 25 , 2006 , and marketed with the tagline : `` Is n't it time everyone hears your secrets ? ''

### Document 5

- ID: `fever_99435__semantic_noise__4`
- Role: `semantic_distractor`
- Source: `semantic_noise_from_fever`
- Title: FEVER evidence for claim 217024

Jab_Tak_Hai_Jaan sentence 14: The film was praised for its direction , cinematography , and the chemistry between its lead actors .

### Document 6

- ID: `fever_99435__semantic_noise__5`
- Role: `semantic_distractor`
- Source: `semantic_noise_from_fever`
- Title: FEVER evidence for claim 77869

A_River_Runs_Through_It_-LRB-film-RRB- sentence 5: The film won an Academy Award for Best Cinematography in 1993 and was nominated for two other Oscars , for Best Music , Original Score and Best Adapted Screenplay .

### Document 7

- ID: `fever_99435__semantic_noise__6`
- Role: `semantic_distractor`
- Source: `semantic_noise_from_fever`
- Title: FEVER evidence for claim 138514

The_dress sentence 7: At the same time , members of the scientific community began to investigate the photo for fresh insights into human colour vision .

### Document 8

- ID: `fever_99435__semantic_noise__7`
- Role: `semantic_distractor`
- Source: `semantic_noise_from_fever`
- Title: FEVER evidence for claim 181823

Don_Hall_-LRB-filmmaker-RRB- sentence 0: Don Hall is an American film director and writer at Walt Disney Animation Studios .

**Human judgment:** PASS / FAIL / UNCERTAIN

**Reason:**

---

## Case 16: fever / noisy

**Instance ID:** `fever_43008__noisy`

**Question:** Verify this claim: Argentina has a Congress.

**Gold answer:** SUPPORTS

**Expected abstention:** False

**Evidence:**

### Document 1

- ID: `fever_43008_gold_0`
- Role: `support`
- Source: `fever`
- Title: FEVER evidence for claim 43008

Argentina sentence 3: The country is subdivided into twenty-three provinces -LRB- provincias , singular provincia -RRB- and one autonomous city -LRB- ciudad autónoma -RRB- , Buenos Aires , which is the federal capital of the nation -LRB- -LSB- Capital Federal , links = no -RSB- -RRB- as decided by Congress . National_Congress_of_Argentina sentence 0: The Congress of the Argentine Nation -LRB- Congreso de la Nación Argentina -RRB- is the legislative branch of the government of Argentina .

### Document 2

- ID: `fever_43008__semantic_noise__0`
- Role: `semantic_distractor`
- Source: `semantic_noise_from_fever`
- Title: FEVER evidence for claim 220975

Group_of_15 sentence 4: Chile , Iran and Kenya have since joined the Group of 15 , whereas Yugoslavia is no longer part of the group ; Peru , a founding member-state , decided to leave the G-15 in 2011 .

### Document 3

- ID: `fever_43008__semantic_noise__1`
- Role: `semantic_distractor`
- Source: `semantic_noise_from_fever`
- Title: FEVER evidence for claim 3637

Mormons sentence 24: The number of members in 1971 was 3,090,953 and now in 2017 based on the Annual Report , there are 15,882,417 worldwide .

### Document 4

- ID: `fever_43008__semantic_noise__2`
- Role: `semantic_distractor`
- Source: `semantic_noise_from_fever`
- Title: FEVER evidence for claim 30062

Port_of_Spain sentence 0: Port of Spain is the capital city of the Republic of Trinidad and Tobago and the country 's third-largest municipality , after Chaguanas and San Fernando . Trinidad_and_Tobago sentence 0: Trinidad and Tobago -LRB- -LSB- ˈtrɪnᵻˌdæd_ən_təˈbeɪɡoʊ -RSB- , -LSB- - toʊˈ - -RSB- -RRB- , officially the Republic of Trinidad and Tobago , is a twin island country situated off the northern edge of the South American mainland , lying just 11 km off the coast of northeastern Venezuela and 130 km south of Grenada .

### Document 5

- ID: `fever_43008__semantic_noise__3`
- Role: `semantic_distractor`
- Source: `semantic_noise_from_fever`
- Title: FEVER evidence for claim 164894

Hezbollah sentence 7: Its leaders were followers of Ayatollah Khomeini , and its forces were trained and organized by a contingent of 1,500 Revolutionary Guards that arrived from Iran with permission from the Syrian government , which was in occupation of Lebanon at the time .

### Document 6

- ID: `fever_43008__semantic_noise__4`
- Role: `semantic_distractor`
- Source: `semantic_noise_from_fever`
- Title: FEVER evidence for claim 43641

Charles_de_Gaulle sentence 2: In 1958 , he founded the Fifth Republic and was elected as the President of France , a position he held until his resignation in 1969 . French_Fifth_Republic sentence 2: De Gaulle , who was the first president elected under the Fifth Republic in December 1958 , believed in a strong head of state , which he described as embodying l'esprit de la nation -LRB- `` the spirit of the nation '' -RRB- .

### Document 7

- ID: `fever_43008__semantic_noise__5`
- Role: `semantic_distractor`
- Source: `semantic_noise_from_fever`
- Title: FEVER evidence for claim 173049

Barcelona sentence 0: Barcelona -LRB- -LSB- bɑrsəˈloʊnə -RSB- , -LSB- bəɾsəˈlonə -RSB- , -LSB- barθeˈlona -RSB- -RRB- is the capital city of the autonomous community of Catalonia in the Kingdom of Spain , as well as the country 's second most populous municipality , with a population of 1.6 million within city limits .

### Document 8

- ID: `fever_43008__semantic_noise__6`
- Role: `semantic_distractor`
- Source: `semantic_noise_from_fever`
- Title: FEVER evidence for claim 8830

Helmand_Province sentence 3: Lashkar Gah serves as the provincial capital .

### Document 9

- ID: `fever_43008__semantic_noise__7`
- Role: `semantic_distractor`
- Source: `semantic_noise_from_fever`
- Title: FEVER evidence for claim 101322

University_of_Mississippi sentence 4: About 55 percent of its undergraduates and 60 percent overall come from Mississippi , and 23 percent are minorities ; international students come from 90 nations .

**Human judgment:** PASS / FAIL / UNCERTAIN

**Reason:**

---

## Case 17: fever / partial

**Instance ID:** `fever_217680__partial`

**Question:** Verify this claim: The Pelican Brief is based solely on a television series.

**Gold answer:** REFUTES

**Expected abstention:** True

**Retained ratio:** 0.41875

**Evidence:**

### Document 1

- ID: `fever_217680__partial__fever_217680_gold_0`
- Role: `partial_support`
- Source: `fever_partial_v3`
- Title: FEVER evidence for claim 217680 | partial evidence

The_Pelican_Brief_-LRB-film-RRB- sentence 0: The Pelican Brief is a

### Document 2

- ID: `fever_217680__semantic_noise__0`
- Role: `semantic_distractor`
- Source: `semantic_noise_from_fever`
- Title: FEVER evidence for claim 5314

Younger_-LRB-TV_series-RRB- sentence 0: Younger is an American single-camera comedy-drama television series based on the Pamela Redmond Satran novel of the same name , created and produced by Darren Star .

### Document 3

- ID: `fever_217680__semantic_noise__1`
- Role: `semantic_distractor`
- Source: `semantic_noise_from_fever`
- Title: FEVER evidence for claim 73716

Psych sentence 0: Psych is an American detective comedy-drama television series created by Steve Franks and broadcast on USA Network with syndicated reruns on ION Television .

**Human judgment:** PASS / FAIL / UNCERTAIN

**Reason:**

---

## Case 18: fever / stale

**Instance ID:** `fever_8830__stale`

**Question:** Verify this claim: Helmand Province is far away from Lashkargah.

**Gold answer:** REFUTES

**Expected abstention:** True

**Evidence:**

### Document 1

- ID: `fever_8830__stale_doc`
- Role: `stale`
- Source: `synthetic_controlled_stale_v3`
- Title: Archived source snapshot (2018)

Snapshot date: 2018-06-30. Question recorded: Verify this claim: Helmand Province is far away from Lashkargah. Reported answer in this snapshot: supports

### Document 2

- ID: `fever_8830__semantic_noise__0`
- Role: `semantic_distractor`
- Source: `semantic_noise_from_fever`
- Title: FEVER evidence for claim 164894

Hezbollah sentence 7: Its leaders were followers of Ayatollah Khomeini , and its forces were trained and organized by a contingent of 1,500 Revolutionary Guards that arrived from Iran with permission from the Syrian government , which was in occupation of Lebanon at the time .

### Document 3

- ID: `fever_8830__semantic_noise__1`
- Role: `semantic_distractor`
- Source: `semantic_noise_from_fever`
- Title: FEVER evidence for claim 228432

The_Wallace_-LRB-poem-RRB- sentence 2: The poem is historically inaccurate , and mentions several events that never happened .

### Document 4

- ID: `fever_8830__semantic_noise__2`
- Role: `semantic_distractor`
- Source: `semantic_noise_from_fever`
- Title: FEVER evidence for claim 75025

Melilla sentence 0: Melilla -LRB- -LSB- məˈliːjə -RSB- ; -LSB- meˈliʎa -RSB- , -LSB- meˈliʝa -RSB- ; Mřič -LSB- , Maliliyyah -RRB- is a Spanish autonomous city located on the north coast of Africa , sharing a border with Morocco with an area of 12.3 km2 .

### Document 5

- ID: `fever_8830__semantic_noise__3`
- Role: `semantic_distractor`
- Source: `semantic_noise_from_fever`
- Title: FEVER evidence for claim 220975

Group_of_15 sentence 4: Chile , Iran and Kenya have since joined the Group of 15 , whereas Yugoslavia is no longer part of the group ; Peru , a founding member-state , decided to leave the G-15 in 2011 .

### Document 6

- ID: `fever_8830__semantic_noise__4`
- Role: `semantic_distractor`
- Source: `semantic_noise_from_fever`
- Title: FEVER evidence for claim 142948

Mount_Rushmore sentence 15: Lack of funding forced construction to end in late October 1941 .

### Document 7

- ID: `fever_8830__semantic_noise__5`
- Role: `semantic_distractor`
- Source: `semantic_noise_from_fever`
- Title: FEVER evidence for claim 173657

Moesia sentence 1: It included most of the territory of modern-day Central Serbia and the northern parts of the modern Republic of Macedonia -LRB- Moesia Superior -RRB- , as well Northern Bulgaria and Romanian Dobrudja -LRB- Moesia Inferior -RRB- .

### Document 8

- ID: `fever_8830__semantic_noise__6`
- Role: `semantic_distractor`
- Source: `semantic_noise_from_fever`
- Title: FEVER evidence for claim 49405

Temple_Mount sentence 1: It has been venerated as a holy site for thousands of years by Judaism , Christianity , and Islam .

### Document 9

- ID: `fever_8830__semantic_noise__7`
- Role: `semantic_distractor`
- Source: `semantic_noise_from_fever`
- Title: FEVER evidence for claim 149369

Therasia sentence 0: Therasia , also known as Thirasía , is an island in the volcanic island group of Santorini in the Greek Cyclades .

**Human judgment:** PASS / FAIL / UNCERTAIN

**Reason:**

---

## Case 19: finqa / clean

**Instance ID:** `finqa_338__clean`

**Question:** what is the change in total debt to be repaid in the contractual obligations for future payments under existing debt and lease commitments and purchase obligations at december 31 , 2005 between 2008 and 2007?

**Gold answer:** -262.0

**Expected abstention:** False

**Evidence:**

### Document 1

- ID: `finqa_338_gold_0`
- Role: `support`
- Source: `finqa`
- Title: FinQA report item IP/2005/page_35.pdf-2

contractual obligations for future payments under existing debt and lease commitments and purchase obli- gations at december 31 , 2005 , were as follows : in millions 2006 2007 2008 2009 2010 thereafter . Financial table: in millions | 2006 | 2007 | 2008 | 2009 | 2010 | thereafter total debt | $ 1181 | $ 570 | $ 308 | $ 2330 | $ 1534 | $ 6281 lease obligations | 172 | 144 | 119 | 76 | 63 | 138 purchase obligations ( a ) | 3264 | 393 | 280 | 240 | 204 | 1238 total | $ 4617 | $ 1107 | $ 707 | $ 2646 | $ 1801 | $ 7657 ( a ) the 2006 amount includes $ 2.4 billion for contracts made in the ordinary course of business to purchase pulpwood , logs and wood chips . the majority of our other purchase obligations are take-or-pay or purchase commitments made in the ordinary course of business related to raw material purchases and energy contracts . other significant items include purchase obligations related to contracted services . transformation plan in july 2005 , the company announced a plan to focus its business portfolio on two key global platform businesses : uncoated papers ( including distribution ) and packaging . the plan also focuses on improving shareholder return through mill rea ...

**Human judgment:** PASS / FAIL / UNCERTAIN

**Reason:**

---

## Case 20: finqa / contradictory

**Instance ID:** `finqa_178__contradictory`

**Question:** net cash provided by operating activities increased by what percentage in 2014?

**Gold answer:** 0.19151

**Expected abstention:** True

**Evidence:**

### Document 1

- ID: `finqa_178_gold_0`
- Role: `support`
- Source: `finqa`
- Title: FinQA report item AES/2015/page_117.pdf-4

proportional free cash flow ( a non-gaap measure ) we define proportional free cash flow as cash flows from operating activities less maintenance capital expenditures ( including non-recoverable environmental capital expenditures ) , adjusted for the estimated impact of noncontrolling interests . upon the company's adoption of the accounting guidance for service concession arrangements effective january 1 , 2015 , capital expenditures related to service concession assets that would have been classified as investing activities on the consolidated statement of cash flows are now classified as operating activities . beginning in the quarter ended march 31 , 2015 , the company changed the definition of proportional free cash flow to exclude the cash flows for capital expenditures related to service concession assets that are now classified within net cash provided by operating activities on the consolidated statement of cash flows . the proportional adjustment factor for these capital expenditures is presented in the reconciliation below . Financial table: calculation of proportional free cash flow ( in millions ) | 2015 | 2014 | 2013 | 2015/2014 change | 2014/2013 change net cash prov ...

### Document 2

- ID: `finqa_178__contradictory_doc`
- Role: `contradictory`
- Source: `synthetic_controlled_contradiction_v3`
- Title: Independent retrieved record

Question recorded: net cash provided by operating activities increased by what percentage in 2014? Reported answer: -0.1634

### Document 3

- ID: `finqa_178__semantic_noise__0`
- Role: `semantic_distractor`
- Source: `semantic_noise_from_finqa`
- Title: FinQA report item UNP/2014/page_35.pdf-2

we have adequate access to capital markets to meet any foreseeable cash requirements , and we have sufficient financial capacity to satisfy our current liabilities . cash flows millions 2014 2013 2012 . Financial table: cash flowsmillions | 2014 | 2013 | 2012 cash provided by operating activities | $ 7385 | $ 6823 | $ 6161 cash used in investing activities | -4249 ( 4249 ) | -3405 ( 3405 ) | -3633 ( 3633 ) cash used in financing activities | -2982 ( 2982 ) | -3049 ( 3049 ) | -2682 ( 2682 ) net change in cash and cashequivalents | $ 154 | $ 369 | $ -154 ( 154 ) operating activities higher net income in 2014 increased cash provided by operating activities compared to 2013 , despite higher income tax payments . 2014 income tax payments were higher than 2013 primarily due to higher income , but also because we paid taxes previously deferred by bonus depreciation ( discussed below ) . higher net income in 2013 increased cash provided by operating activities compared to 2012 . in addition , we made payments in 2012 for past wages as a result of national labor negotiations , which reduced cash provided by operating activities in 2012 . lower tax benefits from bonus depreciation ( as discu ...

### Document 4

- ID: `finqa_178__semantic_noise__1`
- Role: `semantic_distractor`
- Source: `semantic_noise_from_finqa`
- Title: FinQA report item LMT/2010/page_42.pdf-4

( in millions ) 2010 2009 2008 . Financial table: ( in millions ) | 2010 | 2009 | 2008 net cash provided by operating activities | $ 3547 | $ 3173 | $ 4421 net cash used for investing activities | -319 ( 319 ) | -1518 ( 1518 ) | -907 ( 907 ) net cash used for financing activities | -3363 ( 3363 ) | -1476 ( 1476 ) | -3938 ( 3938 ) operating activities net cash provided by operating activities increased by $ 374 million to $ 3547 million in 2010 as compared to 2009 . the increase primarily was attributable to an improvement in our operating working capital balances of $ 570 million as discussed below , and $ 187 million related to lower net income tax payments , as compared to 2009 . partially offsetting these improvements was a net reduction in cash from operations of $ 350 million related to our defined benefit pension plan . this reduction was the result of increased contributions to the pension trust of $ 758 million as compared to 2009 , partially offset by an increase in the cas costs recovered on our contracts . operating working capital accounts consists of receivables , inventories , accounts payable , and customer advances and amounts in excess of costs incurred . the impro ...

**Human judgment:** PASS / FAIL / UNCERTAIN

**Reason:**

---

## Case 21: finqa / missing

**Instance ID:** `finqa_378__missing`

**Question:** what was the ratio of the debts to the assets in the purchase transaction

**Gold answer:** 0.17792

**Expected abstention:** True

**Evidence:**

### Document 1

- ID: `finqa_378__semantic_noise__0`
- Role: `semantic_distractor`
- Source: `semantic_noise_from_finqa`
- Title: FinQA report item GPN/2009/page_70.pdf-2

notes to consolidated financial statements 2014 ( continued ) in connection with these discover related purchases , we have sold the contractual rights to future commissions on discover transactions to certain of our isos . contractual rights sold totaled $ 7.6 million during the year ended may 31 , 2008 and $ 1.0 million during fiscal 2009 . such sale proceeds are generally collected in installments over periods ranging from three to nine months . during fiscal 2009 , we collected $ 4.4 million of such proceeds , which are included in the proceeds from sale of investment and contractual rights in our consolidated statement of cash flows . we do not recognize gains on these sales of contractual rights at the time of sale . proceeds are deferred and recognized as a reduction of the related commission expense . during fiscal 2009 , we recognized $ 1.2 million of such deferred sales proceeds as other long-term liabilities . other 2008 acquisitions during fiscal 2008 , we acquired a majority of the assets of euroenvios money transfer , s.a . Financial table: | total goodwill | $ 13536 customer-related intangible assets | 4091 contract-based intangible assets | 1031 property and equipme ...

### Document 2

- ID: `finqa_378__semantic_noise__1`
- Role: `semantic_distractor`
- Source: `semantic_noise_from_finqa`
- Title: FinQA report item BDX/2019/page_45.pdf-1

debt-related activities certain measures relating to our total debt were as follows: . Financial table: | 2019 | 2018 | 2017 total debt ( millions of dollars ) | $ 19390 | $ 21496 | $ 18870 short-term debt as a percentage of total debt | 6.8% ( 6.8 % ) | 12.1% ( 12.1 % ) | 1.1% ( 1.1 % ) weighted average cost of total debt | 2.9% ( 2.9 % ) | 3.2% ( 3.2 % ) | 3.3% ( 3.3 % ) total debt as a percentage of total capital ( a ) | 45.6% ( 45.6 % ) | 47.8% ( 47.8 % ) | 57.5% ( 57.5 % ) ( a ) represents shareholders 2019 equity , net non-current deferred income tax liabilities , and debt . the decrease in short-term debt as a percentage of total debt at september 30 , 2019 was primarily driven by the payment of certain short-term notes as well as the issuance of long-term notes in 2019 . the increase in short-term debt as a percentage of total debt at september 30 , 2018 was primarily driven by the reclassification of certain notes from long-term to short-term . additional disclosures regarding our debt instruments are provided in note 16 to the consolidated financial statements contained in item 8 . financial statements and supplementary data . cash and short-term investments at september  ...

### Document 3

- ID: `finqa_378__semantic_noise__2`
- Role: `semantic_distractor`
- Source: `semantic_noise_from_finqa`
- Title: FinQA report item PKG/2009/page_65.pdf-2

purchase commitments the company has entered into various purchase agreements for minimum amounts of pulpwood processing and energy over periods ranging from one to twenty years at fixed prices . total purchase commitments are as follows: . Financial table: | ( in thousands ) 2010 | $ 6951 2011 | 5942 2012 | 3659 2013 | 1486 2014 | 1486 thereafter | 25048 total | $ 44572 these purchase agreements are not marked to market . the company purchased $ 37.3 million , $ 29.4 million , and $ 14.5 million during the years ended december 31 , 2009 , 2008 and 2007 , respectively , under these purchase agreements . litigation pca is a party to various legal actions arising in the ordinary course of business . these legal actions cover a broad variety of claims spanning our entire business . as of the date of this filing , the company believes it is not reasonably possible that the resolution of these legal actions will , individually or in the aggregate , have a material adverse effect on its financial position , results of operations , or cash flows . environmental liabilities the potential costs for various environmental matters are uncertain due to such factors as the unknown magnitude of p ...

### Document 4

- ID: `finqa_378__semantic_noise__3`
- Role: `semantic_distractor`
- Source: `semantic_noise_from_finqa`
- Title: FinQA report item PKG/2009/page_65.pdf-3

purchase commitments the company has entered into various purchase agreements for minimum amounts of pulpwood processing and energy over periods ranging from one to twenty years at fixed prices . total purchase commitments are as follows: . Financial table: | ( in thousands ) 2010 | $ 6951 2011 | 5942 2012 | 3659 2013 | 1486 2014 | 1486 thereafter | 25048 total | $ 44572 these purchase agreements are not marked to market . the company purchased $ 37.3 million , $ 29.4 million , and $ 14.5 million during the years ended december 31 , 2009 , 2008 and 2007 , respectively , under these purchase agreements . litigation pca is a party to various legal actions arising in the ordinary course of business . these legal actions cover a broad variety of claims spanning our entire business . as of the date of this filing , the company believes it is not reasonably possible that the resolution of these legal actions will , individually or in the aggregate , have a material adverse effect on its financial position , results of operations , or cash flows . environmental liabilities the potential costs for various environmental matters are uncertain due to such factors as the unknown magnitude of p ...

### Document 5

- ID: `finqa_378__semantic_noise__4`
- Role: `semantic_distractor`
- Source: `semantic_noise_from_finqa`
- Title: FinQA report item PKG/2009/page_65.pdf-1

purchase commitments the company has entered into various purchase agreements for minimum amounts of pulpwood processing and energy over periods ranging from one to twenty years at fixed prices . total purchase commitments are as follows: . Financial table: | ( in thousands ) 2010 | $ 6951 2011 | 5942 2012 | 3659 2013 | 1486 2014 | 1486 thereafter | 25048 total | $ 44572 these purchase agreements are not marked to market . the company purchased $ 37.3 million , $ 29.4 million , and $ 14.5 million during the years ended december 31 , 2009 , 2008 and 2007 , respectively , under these purchase agreements . litigation pca is a party to various legal actions arising in the ordinary course of business . these legal actions cover a broad variety of claims spanning our entire business . as of the date of this filing , the company believes it is not reasonably possible that the resolution of these legal actions will , individually or in the aggregate , have a material adverse effect on its financial position , results of operations , or cash flows . environmental liabilities the potential costs for various environmental matters are uncertain due to such factors as the unknown magnitude of p ...

### Document 6

- ID: `finqa_378__semantic_noise__5`
- Role: `semantic_distractor`
- Source: `semantic_noise_from_finqa`
- Title: FinQA report item BLL/2007/page_47.pdf-4

page 31 of 94 other liquidity items cash payments required for long-term debt maturities , rental payments under noncancellable operating leases , purchase obligations and other commitments in effect at december 31 , 2007 , are summarized in the following table: . Financial table: ( $ in millions ) | payments due by period ( a ) total | payments due by period ( a ) less than 1 year | payments due by period ( a ) 1-3 years | payments due by period ( a ) 3-5 years | payments due by period ( a ) more than 5 years long-term debt | $ 2302.6 | $ 126.1 | $ 547.6 | $ 1174.9 | $ 454.0 capital lease obligations | 4.4 | 1.0 | 0.8 | 0.5 | 2.1 interest payments on long-term debt ( b ) | 698.6 | 142.9 | 246.3 | 152.5 | 156.9 operating leases | 218.5 | 49.9 | 71.7 | 42.5 | 54.4 purchase obligations ( c ) | 6092.6 | 2397.2 | 3118.8 | 576.6 | 2013 common stock repurchase agreements | 131.0 | 131.0 | 2013 | 2013 | 2013 legal settlement | 70.0 | 70.0 | 2013 | 2013 | 2013 total payments on contractual obligations | $ 9517.7 | $ 2918.1 | $ 3985.2 | $ 1947.0 | $ 667.4 total payments on contractual obligations $ 9517.7 $ 2918.1 $ 3985.2 $ 1947.0 $ 667.4 ( a ) amounts reported in local currencies have bee ...

### Document 7

- ID: `finqa_378__semantic_noise__6`
- Role: `semantic_distractor`
- Source: `semantic_noise_from_finqa`
- Title: FinQA report item ABMD/2009/page_56.pdf-3

additionally , we incurred $ 3.8 million related to cash expenditures for property and equipment primarily on computer software projects and manufacturing equipment related to our expansion in ireland . cash provided by financing activities for the year ended march 31 , 2009 was primarily comprised of $ 42.0 million in net proceeds related to our august 2008 public offering and $ 5.0 million attributable to the exercise of stock options and proceeds from our employee stock purchase plan . capital expenditures for fiscal 2010 are estimated to be $ 2.5 to $ 3.0 million , which relate primarily to our planned manufacturing capacity increases for impella in germany , our expansion in ireland , and software development projects . factors that may affect liquidity include our ability to penetrate the market for our products , maintain or reduce the length of the selling cycle , and collect cash from clients after our products are sold . exclusive of activities involving any future acquisitions of products or companies that complement or augment our existing line of products , we believe that current available funds and cash generated from operations will provide sufficient liquidity to m ...

### Document 8

- ID: `finqa_378__semantic_noise__7`
- Role: `semantic_distractor`
- Source: `semantic_noise_from_finqa`
- Title: FinQA report item IP/2005/page_35.pdf-4

contractual obligations for future payments under existing debt and lease commitments and purchase obli- gations at december 31 , 2005 , were as follows : in millions 2006 2007 2008 2009 2010 thereafter . Financial table: in millions | 2006 | 2007 | 2008 | 2009 | 2010 | thereafter total debt | $ 1181 | $ 570 | $ 308 | $ 2330 | $ 1534 | $ 6281 lease obligations | 172 | 144 | 119 | 76 | 63 | 138 purchase obligations ( a ) | 3264 | 393 | 280 | 240 | 204 | 1238 total | $ 4617 | $ 1107 | $ 707 | $ 2646 | $ 1801 | $ 7657 ( a ) the 2006 amount includes $ 2.4 billion for contracts made in the ordinary course of business to purchase pulpwood , logs and wood chips . the majority of our other purchase obligations are take-or-pay or purchase commitments made in the ordinary course of business related to raw material purchases and energy contracts . other significant items include purchase obligations related to contracted services . transformation plan in july 2005 , the company announced a plan to focus its business portfolio on two key global platform businesses : uncoated papers ( including distribution ) and packaging . the plan also focuses on improving shareholder return through mill rea ...

**Human judgment:** PASS / FAIL / UNCERTAIN

**Reason:**

---

## Case 22: finqa / noisy

**Instance ID:** `finqa_108__noisy`

**Question:** for the quarter ended march 312008 what was the percent of the change from the highest to the lowest of the company per share sale prices of common stock

**Gold answer:** 0.33084

**Expected abstention:** False

**Evidence:**

### Document 1

- ID: `finqa_108_gold_0`
- Role: `support`
- Source: `finqa`
- Title: FinQA report item AMT/2008/page_32.pdf-3

part ii item 5 . market for registrant 2019s common equity , related stockholder matters and issuer purchases of equity securities the following table presents reported quarterly high and low per share sale prices of our common stock on the new york stock exchange ( 201cnyse 201d ) for the years 2008 and 2007. . Financial table: 2008 | high | low quarter ended march 31 | $ 42.72 | $ 32.10 quarter ended june 30 | 46.10 | 38.53 quarter ended september 30 | 43.43 | 31.89 quarter ended december 31 | 37.28 | 19.35 2007 | high | low quarter ended march 31 | $ 41.31 | $ 36.63 quarter ended june 30 | 43.84 | 37.64 quarter ended september 30 | 45.45 | 36.34 quarter ended december 31 | 46.53 | 40.08 on february 13 , 2009 , the closing price of our common stock was $ 28.85 per share as reported on the nyse . as of february 13 , 2009 , we had 397097677 outstanding shares of common stock and 499 registered holders . dividends we have never paid a dividend on our common stock . we anticipate that we may retain future earnings , if any , to fund the development and growth of our business . the indentures governing our 7.50% ( 7.50 % ) senior notes due 2012 ( 201c7.50% ( 201c7.50 % ) notes 201d )  ...

### Document 2

- ID: `finqa_108__semantic_noise__0`
- Role: `semantic_distractor`
- Source: `semantic_noise_from_finqa`
- Title: FinQA report item AMT/2010/page_34.pdf-4

part ii item 5 . market for registrant 2019s common equity , related stockholder matters and issuer purchases of equity securities the following table presents reported quarterly high and low per share sale prices of our common stock on the new york stock exchange ( 201cnyse 201d ) for the years 2010 and 2009. . Financial table: 2010 | high | low quarter ended march 31 | $ 44.61 | $ 40.10 quarter ended june 30 | 45.33 | 38.86 quarter ended september 30 | 52.11 | 43.70 quarter ended december 31 | 53.14 | 49.61 2009 | high | low quarter ended march 31 | $ 32.53 | $ 25.45 quarter ended june 30 | 34.52 | 27.93 quarter ended september 30 | 37.71 | 29.89 quarter ended december 31 | 43.84 | 35.03 on february 11 , 2011 , the closing price of our common stock was $ 56.73 per share as reported on the nyse . as of february 11 , 2011 , we had 397612895 outstanding shares of common stock and 463 registered holders . dividends we have not historically paid a dividend on our common stock . payment of dividends in the future , when , as and if authorized by our board of directors , would depend upon many factors , including our earnings and financial condition , restrictions under applicable law a ...

### Document 3

- ID: `finqa_108__semantic_noise__1`
- Role: `semantic_distractor`
- Source: `semantic_noise_from_finqa`
- Title: FinQA report item AMT/2008/page_32.pdf-1

part ii item 5 . market for registrant 2019s common equity , related stockholder matters and issuer purchases of equity securities the following table presents reported quarterly high and low per share sale prices of our common stock on the new york stock exchange ( 201cnyse 201d ) for the years 2008 and 2007. . Financial table: 2008 | high | low quarter ended march 31 | $ 42.72 | $ 32.10 quarter ended june 30 | 46.10 | 38.53 quarter ended september 30 | 43.43 | 31.89 quarter ended december 31 | 37.28 | 19.35 2007 | high | low quarter ended march 31 | $ 41.31 | $ 36.63 quarter ended june 30 | 43.84 | 37.64 quarter ended september 30 | 45.45 | 36.34 quarter ended december 31 | 46.53 | 40.08 on february 13 , 2009 , the closing price of our common stock was $ 28.85 per share as reported on the nyse . as of february 13 , 2009 , we had 397097677 outstanding shares of common stock and 499 registered holders . dividends we have never paid a dividend on our common stock . we anticipate that we may retain future earnings , if any , to fund the development and growth of our business . the indentures governing our 7.50% ( 7.50 % ) senior notes due 2012 ( 201c7.50% ( 201c7.50 % ) notes 201d )  ...

### Document 4

- ID: `finqa_108__semantic_noise__2`
- Role: `semantic_distractor`
- Source: `semantic_noise_from_finqa`
- Title: FinQA report item AES/2002/page_46.pdf-3

part ii item 5 2014market for registrant 2019s common equity and related stockholder matters market information . the common stock of the company is currently traded on the new york stock exchange ( nyse ) under the symbol 2018 2018aes . 2019 2019 the following tables set forth the high and low sale prices for the common stock as reported by the nyse for the periods indicated . price range of common stock . Financial table: 2002 first quarter | high $ 17.84 | low $ 4.11 | 2001 first quarter | high $ 60.15 | low $ 41.30 second quarter | 9.17 | 3.55 | second quarter | 52.25 | 39.95 third quarter | 4.61 | 1.56 | third quarter | 44.50 | 12.00 fourth quarter | 3.57 | 0.95 | fourth quarter | 17.80 | 11.60 holders . as of march 3 , 2003 , there were 9663 record holders of the company 2019s common stock , par value $ 0.01 per share . dividends . under the terms of the company 2019s senior secured credit facilities entered into with a commercial bank syndicate , the company is not allowed to pay cash dividends . in addition , the company is precluded from paying cash dividends on its common stock under the terms of a guaranty to the utility customer in connection with the aes thames project ...

### Document 5

- ID: `finqa_108__semantic_noise__3`
- Role: `semantic_distractor`
- Source: `semantic_noise_from_finqa`
- Title: FinQA report item VTR/2007/page_47.pdf-2

as of february 15 , 2008 , there were 138311810 shares of our common stock outstanding held by approximately 2979 stockholders of record . dividends and distributions we pay regular quarterly dividends to holders of our common stock . on february 13 , 2008 , our board of directors declared the first quarterly installment of our 2008 dividend in the amount of $ 0.5125 per share , payable on march 28 , 2008 to stockholders of record on march 6 , 2008 . we expect to distribute 100% ( 100 % ) or more of our taxable net income to our stockholders for 2008 . our board of directors normally makes decisions regarding the frequency and amount of our dividends on a quarterly basis . because the board considers a number of factors when making these decisions , we cannot assure you that we will maintain the policy stated above . please see 201ccautionary statements 201d and the risk factors included in part i , item 1a of this annual report on form 10-k for a description of other factors that may affect our distribution policy . our stockholders may reinvest all or a portion of any cash distribution on their shares of our common stock by participating in our distribution reinvestment and stock ...

### Document 6

- ID: `finqa_108__semantic_noise__4`
- Role: `semantic_distractor`
- Source: `semantic_noise_from_finqa`
- Title: FinQA report item VTR/2007/page_47.pdf-4

as of february 15 , 2008 , there were 138311810 shares of our common stock outstanding held by approximately 2979 stockholders of record . dividends and distributions we pay regular quarterly dividends to holders of our common stock . on february 13 , 2008 , our board of directors declared the first quarterly installment of our 2008 dividend in the amount of $ 0.5125 per share , payable on march 28 , 2008 to stockholders of record on march 6 , 2008 . we expect to distribute 100% ( 100 % ) or more of our taxable net income to our stockholders for 2008 . our board of directors normally makes decisions regarding the frequency and amount of our dividends on a quarterly basis . because the board considers a number of factors when making these decisions , we cannot assure you that we will maintain the policy stated above . please see 201ccautionary statements 201d and the risk factors included in part i , item 1a of this annual report on form 10-k for a description of other factors that may affect our distribution policy . our stockholders may reinvest all or a portion of any cash distribution on their shares of our common stock by participating in our distribution reinvestment and stock ...

### Document 7

- ID: `finqa_108__semantic_noise__5`
- Role: `semantic_distractor`
- Source: `semantic_noise_from_finqa`
- Title: FinQA report item VLO/2018/page_25.pdf-3

table of contents tceq and harris county pollution control services department ( hcpcs ) ( houston terminal ) . we have an outstanding noe from the tceq and an outstanding vn from the hcpcs alleging excess emissions from tank 003 that occurred during hurricane harvey . we are working with the pertinent authorities to resolve these matters . item 4 . mine safety disclosures part ii item 5 . market for registrant 2019s common equity , related stockholder matters and issuer purchases of equity securities our common stock trades on the nyse under the trading symbol 201cvlo . 201d as of january 31 , 2019 , there were 5271 holders of record of our common stock . dividends are considered quarterly by the board of directors , may be paid only when approved by the board , and will depend on our financial condition , results of operations , cash flows , prospects , industry conditions , capital requirements , and other factors and restrictions our board deems relevant . there can be no assurance that we will pay a dividend at the rates we have paid historically , or at all , in the future . Financial table: period | total numberof sharespurchased | averageprice paidper share | total number o ...

### Document 8

- ID: `finqa_108__semantic_noise__6`
- Role: `semantic_distractor`
- Source: `semantic_noise_from_finqa`
- Title: FinQA report item HWM/2017/page_41.pdf-2

part ii item 5 . market for registrant 2019s common equity , related stockholder matters and issuer purchases of equity securities . the company 2019s common stock is listed on the new york stock exchange . prior to the separation of alcoa corporation from the company , the company 2019s common stock traded under the symbol 201caa . 201d in connection with the separation , on november 1 , 2016 , the company changed its stock symbol and its common stock began trading under the symbol 201carnc . 201d on october 5 , 2016 , the company 2019s common shareholders approved a 1-for-3 reverse stock split of the company 2019s outstanding and authorized shares of common stock ( the 201creverse stock split 201d ) . as a result of the reverse stock split , every three shares of issued and outstanding common stock were combined into one issued and outstanding share of common stock , without any change in the par value per share . the reverse stock split reduced the number of shares of common stock outstanding from approximately 1.3 billion shares to approximately 0.4 billion shares , and proportionately decreased the number of authorized shares of common stock from 1.8 billion to 0.6 billion sha ...

### Document 9

- ID: `finqa_108__semantic_noise__7`
- Role: `semantic_distractor`
- Source: `semantic_noise_from_finqa`
- Title: FinQA report item BLL/2010/page_28.pdf-3

page 15 of 100 shareholder return performance the line graph below compares the annual percentage change in ball corporation 2019s cumulative total shareholder return on its common stock with the cumulative total return of the dow jones containers & packaging index and the s&p composite 500 stock index for the five-year period ended december 31 , 2010 . it assumes $ 100 was invested on december 31 , 2005 , and that all dividends were reinvested . the dow jones containers & packaging index total return has been weighted by market capitalization . total return analysis . Financial table: | 12/31/05 | 12/31/06 | 12/31/07 | 12/31/08 | 12/31/09 | 12/31/10 ball corporation | $ 100.00 | $ 110.86 | $ 115.36 | $ 107.58 | $ 134.96 | $ 178.93 dj containers & packaging index | $ 100.00 | $ 112.09 | $ 119.63 | $ 75.00 | $ 105.34 | $ 123.56 s&p 500 index | $ 100.00 | $ 115.80 | $ 122.16 | $ 76.96 | $ 97.33 | $ 111.99 copyright a9 2011 standard & poor 2019s a division of the mcgraw-hill companies inc . all rights reserved . ( www.researchdatagroup.com/s&p.htm ) | copyright a9 2011 standard & poor 2019s a division of the mcgraw-hill companies inc . all rights reserved . ( www.researchdatagroup.com ...

**Human judgment:** PASS / FAIL / UNCERTAIN

**Reason:**

---

## Case 23: finqa / partial

**Instance ID:** `finqa_685__partial`

**Question:** for 2016 , what was the total african and us net undeveloped acres expiring , in thousands ? \\n

**Gold answer:** 257.0

**Expected abstention:** True

**Retained ratio:** 0.5829508196721311

**Evidence:**

### Document 1

- ID: `finqa_685__partial__finqa_685_gold_0`
- Role: `partial_support`
- Source: `finqa_partial_v3`
- Title: FinQA report item MRO/2015/page_18.pdf-1 | partial evidence

in the ordinary course of business , based on our evaluations of certain geologic trends and prospective economics , we have allowed certain lease acreage to expire and may allow additional acreage to expire in the future . if production is not established or we take no other action to extend the terms of the leases , licenses or concessions , undeveloped acreage listed in the table below will expire over the next three years . the kenya transaction closed in february 2016 and the ethiopia transaction is expected to close in the first quarter of 2016 . see item 8 . financial statements and supplementary data - note 5 to the consolidated financial statements for additional information about this disposition . | 68 | 89 | 128 e.g . | 2014 | 92 | 36 other africa | 189 | 4352 | 854 total africa | 189 | 4444 | 890 other international | 2014 | 2014 | 2014 total | 257 | 4533 | 1018 .

### Document 2

- ID: `finqa_685__semantic_noise__0`
- Role: `semantic_distractor`
- Source: `semantic_noise_from_finqa`
- Title: FinQA report item MRO/2015/page_18.pdf-4

in the ordinary course of business , based on our evaluations of certain geologic trends and prospective economics , we have allowed certain lease acreage to expire and may allow additional acreage to expire in the future . if production is not established or we take no other action to extend the terms of the leases , licenses or concessions , undeveloped acreage listed in the table below will expire over the next three years . we plan to continue the terms of certain of these licenses and concession areas or retain leases through operational or administrative actions ; however , the majority of the undeveloped acres associated with other africa as listed in the table below pertains to our licenses in ethiopia and kenya , for which we executed agreements in 2015 to sell . the kenya transaction closed in february 2016 and the ethiopia transaction is expected to close in the first quarter of 2016 . see item 8 . financial statements and supplementary data - note 5 to the consolidated financial statements for additional information about this disposition . net undeveloped acres expiring year ended december 31 . Financial table: ( in thousands ) | net undeveloped acres expiring year end ...

### Document 3

- ID: `finqa_685__semantic_noise__1`
- Role: `semantic_distractor`
- Source: `semantic_noise_from_finqa`
- Title: FinQA report item MRO/2015/page_18.pdf-3

in the ordinary course of business , based on our evaluations of certain geologic trends and prospective economics , we have allowed certain lease acreage to expire and may allow additional acreage to expire in the future . if production is not established or we take no other action to extend the terms of the leases , licenses or concessions , undeveloped acreage listed in the table below will expire over the next three years . we plan to continue the terms of certain of these licenses and concession areas or retain leases through operational or administrative actions ; however , the majority of the undeveloped acres associated with other africa as listed in the table below pertains to our licenses in ethiopia and kenya , for which we executed agreements in 2015 to sell . the kenya transaction closed in february 2016 and the ethiopia transaction is expected to close in the first quarter of 2016 . see item 8 . financial statements and supplementary data - note 5 to the consolidated financial statements for additional information about this disposition . net undeveloped acres expiring year ended december 31 . Financial table: ( in thousands ) | net undeveloped acres expiring year end ...

**Human judgment:** PASS / FAIL / UNCERTAIN

**Reason:**

---

## Case 24: finqa / stale

**Instance ID:** `finqa_255__stale`

**Question:** what percent increase in net income was experienced between 2015 and 2016

**Gold answer:** 0.06507

**Expected abstention:** True

**Evidence:**

### Document 1

- ID: `finqa_255__stale_doc`
- Role: `stale`
- Source: `synthetic_controlled_stale_v3`
- Title: Archived source snapshot (2014)

Snapshot date: 2014-06-30. Question recorded: what percent increase in net income was experienced between 2015 and 2016 Reported answer in this snapshot: 0.04828

### Document 2

- ID: `finqa_255__semantic_noise__0`
- Role: `semantic_distractor`
- Source: `semantic_noise_from_finqa`
- Title: FinQA report item UNP/2015/page_35.pdf-3

at december 31 , 2015 and 2014 , we had a modest working capital surplus . this reflects a strong cash position that provides enhanced liquidity in an uncertain economic environment . in addition , we believe we have adequate access to capital markets to meet any foreseeable cash requirements , and we have sufficient financial capacity to satisfy our current liabilities . cash flows . Financial table: millions | 2015 | 2014 | 2013 cash provided by operating activities | $ 7344 | $ 7385 | $ 6823 cash used in investing activities | -4476 ( 4476 ) | -4249 ( 4249 ) | -3405 ( 3405 ) cash used in financing activities | -3063 ( 3063 ) | -2982 ( 2982 ) | -3049 ( 3049 ) net change in cash and cash equivalents | $ -195 ( 195 ) | $ 154 | $ 369 operating activities cash provided by operating activities decreased in 2015 compared to 2014 due to lower net income and changes in working capital , partially offset by the timing of tax payments . federal tax law provided for 100% ( 100 % ) bonus depreciation for qualified investments made during 2011 and 50% ( 50 % ) bonus depreciation for qualified investments made during 2012-2013 . as a result , the company deferred a substantial portion of its 2 ...

### Document 3

- ID: `finqa_255__semantic_noise__1`
- Role: `semantic_distractor`
- Source: `semantic_noise_from_finqa`
- Title: FinQA report item UAA/2016/page_52.pdf-1

2022 net revenues in our connected fitness operating segment increased $ 34.2 million to $ 53.4 million in 2015 from $ 19.2 million in 2014 primarily due to revenues generated from our two connected fitness acquisitions in 2015 and growth in our existing connected fitness business . operating income ( loss ) by segment is summarized below: . Financial table: ( in thousands ) | year ended december 31 , 2015 | year ended december 31 , 2014 | year ended december 31 , $ change | year ended december 31 , % ( % ) change north america | $ 460961 | $ 372347 | $ 88614 | 23.8% ( 23.8 % ) emea | 3122 | -11763 ( 11763 ) | 14885 | 126.5 asia-pacific | 36358 | 21858 | 14500 | 66.3 latin america | -30593 ( 30593 ) | -15423 ( 15423 ) | -15170 ( 15170 ) | -98.4 ( 98.4 ) connected fitness | -61301 ( 61301 ) | -13064 ( 13064 ) | -48237 ( 48237 ) | -369.2 ( 369.2 ) total operating income | $ 408547 | $ 353955 | $ 54592 | 15.4% ( 15.4 % ) the increase in total operating income was driven by the following : 2022 operating income in our north america operating segment increased $ 88.6 million to $ 461.0 million in 2015 from $ 372.4 million in 2014 primarily due to the items discussed above in the consoli ...

### Document 4

- ID: `finqa_255__semantic_noise__2`
- Role: `semantic_distractor`
- Source: `semantic_noise_from_finqa`
- Title: FinQA report item UAA/2016/page_52.pdf-2

2022 net revenues in our connected fitness operating segment increased $ 34.2 million to $ 53.4 million in 2015 from $ 19.2 million in 2014 primarily due to revenues generated from our two connected fitness acquisitions in 2015 and growth in our existing connected fitness business . operating income ( loss ) by segment is summarized below: . Financial table: ( in thousands ) | year ended december 31 , 2015 | year ended december 31 , 2014 | year ended december 31 , $ change | year ended december 31 , % ( % ) change north america | $ 460961 | $ 372347 | $ 88614 | 23.8% ( 23.8 % ) emea | 3122 | -11763 ( 11763 ) | 14885 | 126.5 asia-pacific | 36358 | 21858 | 14500 | 66.3 latin america | -30593 ( 30593 ) | -15423 ( 15423 ) | -15170 ( 15170 ) | -98.4 ( 98.4 ) connected fitness | -61301 ( 61301 ) | -13064 ( 13064 ) | -48237 ( 48237 ) | -369.2 ( 369.2 ) total operating income | $ 408547 | $ 353955 | $ 54592 | 15.4% ( 15.4 % ) the increase in total operating income was driven by the following : 2022 operating income in our north america operating segment increased $ 88.6 million to $ 461.0 million in 2015 from $ 372.4 million in 2014 primarily due to the items discussed above in the consoli ...

### Document 5

- ID: `finqa_255__semantic_noise__3`
- Role: `semantic_distractor`
- Source: `semantic_noise_from_finqa`
- Title: FinQA report item ETR/2016/page_418.pdf-3

entergy texas , inc . and subsidiaries management 2019s financial discussion and analysis results of operations net income 2016 compared to 2015 net income increased $ 37.9 million primarily due to lower other operation and maintenance expenses , the asset write-off of its receivable associated with the spindletop gas storage facility in 2015 , and higher net revenue . 2015 compared to 2014 net income decreased $ 5.2 million primarily due to the asset write-off of its receivable associated with the spindletop gas storage facility and higher other operation and maintenance expenses , partially offset by higher net revenue and a lower effective tax rate . net revenue 2016 compared to 2015 net revenue consists of operating revenues net of : 1 ) fuel , fuel-related expenses , and gas purchased for resale , 2 ) purchased power expenses , and 3 ) other regulatory charges . following is an analysis of the change in net revenue comparing 2016 to 2015 . amount ( in millions ) . Financial table: | amount ( in millions ) 2015 net revenue | $ 637.2 reserve equalization | 14.3 purchased power capacity | 12.4 transmission revenue | 7.0 retail electric price | 5.4 net wholesale | -27.8 ( 27.8 ) o ...

### Document 6

- ID: `finqa_255__semantic_noise__4`
- Role: `semantic_distractor`
- Source: `semantic_noise_from_finqa`
- Title: FinQA report item LMT/2016/page_48.pdf-4

$ 70 million . since that time , we have continued to experience issues related to customer requirements and the implementation of this contract and have periodically accrued additional reserves . it is possible that we may have to record additional loss reserves in future periods , which could be material to our operating results . our consolidated net adjustments not related to volume , including net profit booking rate adjustments and other matters , net of state income taxes , increased segment operating profit by approximately $ 1.5 billion , $ 1.7 billion and $ 1.6 billion for 2016 , 2015 and 2014 . the decrease in our consolidated net adjustments in 2016 compared to 2015 was primarily due to a decrease in profit booking rate adjustments at our mfc and space systems business segments , partially offset by an increase at our rms business segment . the increase in our consolidated net adjustments in 2015 compared to 2014 was primarily due to an increase in profit booking rate adjustments at our space systems and aeronautics business segments , offset by a decrease in profit booking rate adjustments at our rms and mfc business segments . Financial table: | 2016 | 2015 | 2014 net ...

### Document 7

- ID: `finqa_255__semantic_noise__5`
- Role: `semantic_distractor`
- Source: `semantic_noise_from_finqa`
- Title: FinQA report item APD/2014/page_39.pdf-2

2014 vs . 2013 sales increased 9% ( 9 % ) , as higher volumes of 9% ( 9 % ) and favorable currency of 1% ( 1 % ) were partially offset by lower pricing of 1% ( 1 % ) . electronics sales increased 8% ( 8 % ) , as higher delivery systems equipment sales and materials volumes of 8% ( 8 % ) and favorable currency of 1% ( 1 % ) were partially offset by lower pricing of 1% ( 1 % ) . performance materials sales increased 10% ( 10 % ) , as higher volumes of 11% ( 11 % ) were partially offset by lower pricing of 1% ( 1 % ) . the higher volumes were across all product lines and major regions . the lower pricing was primarily due to unfavorable mix impacts . operating income of $ 425.3 increased 32% ( 32 % ) , or $ 104.0 , primarily from higher volumes of $ 93 , lower operating costs of $ 31 , and favorable currency impacts of $ 5 , partially offset by unfavorable price and mix impacts of $ 26 . operating margin of 17.4% ( 17.4 % ) increased 310 bp , primarily due to improved loading and leverage from the higher volumes and improved cost performance , partially offset by the unfavorable pricing impacts . Financial table: | 2014 | 2013 | 2012 sales | $ 450.4 | $ 451.1 | $ 420.1 operating incom ...

### Document 8

- ID: `finqa_255__semantic_noise__6`
- Role: `semantic_distractor`
- Source: `semantic_noise_from_finqa`
- Title: FinQA report item ETR/2017/page_316.pdf-3

entergy arkansas , inc . and subsidiaries management 2019s financial discussion and analysis results of operations net income 2017 compared to 2016 net income decreased $ 27.4 million primarily due to higher nuclear refueling outage expenses , higher depreciation and amortization expenses , higher taxes other than income taxes , and higher interest expense , partially offset by higher other income . 2016 compared to 2015 net income increased $ 92.9 million primarily due to higher net revenue and lower other operation and maintenance expenses , partially offset by a higher effective income tax rate and higher depreciation and amortization expenses . net revenue 2017 compared to 2016 net revenue consists of operating revenues net of : 1 ) fuel , fuel-related expenses , and gas purchased for resale , 2 ) purchased power expenses , and 3 ) other regulatory charges ( credits ) . a0 a0following is an analysis of the change in net revenue comparing 2017 to 2016 . amount ( in millions ) . Financial table: | amount ( in millions ) 2016 net revenue | $ 1520.5 retail electric price | 33.8 opportunity sales | 5.6 asset retirement obligation | -14.8 ( 14.8 ) volume/weather | -29.0 ( 29.0 ) othe ...

### Document 9

- ID: `finqa_255__semantic_noise__7`
- Role: `semantic_distractor`
- Source: `semantic_noise_from_finqa`
- Title: FinQA report item RE/2015/page_33.pdf-4

the company had net realized capital losses for 2015 of $ 184.1 million . the company 2019s cash and invested assets totaled $ 17.7 billion at december 31 , 2015 , which consisted of 87.4% ( 87.4 % ) fixed maturities and cash , of which 91.4% ( 91.4 % ) were investment grade ; 8.2% ( 8.2 % ) equity securities and 4.4% ( 4.4 % ) other invested assets . the average maturity of fixed maturity securities was 4.1 years at december 31 , 2015 , and their overall duration was 3.0 years . as of december 31 , 2015 , the company did not have any direct investments in commercial real estate or direct commercial mortgages or any material holdings of derivative investments ( other than equity index put option contracts as discussed in item 8 , 201cfinancial statements and supplementary data 201d - note 4 of notes to consolidated financial statements ) or securities of issuers that are experiencing cash flow difficulty to an extent that the company 2019s management believes could threaten the issuer 2019s ability to meet debt service payments , except where other-than-temporary impairments have been recognized . the company 2019s investment portfolio includes structured commercial mortgage-backed ...

**Human judgment:** PASS / FAIL / UNCERTAIN

**Reason:**

---

## Case 25: hotpotqa / clean

**Instance ID:** `hotpotqa_3698__clean`

**Question:** What do Josef Veltjens and Hermann Goering have in common?

**Gold answer:** A veteran World War I fighter pilot ace

**Expected abstention:** False

**Evidence:**

### Document 1

- ID: `hotpotqa_3698_gold_0`
- Role: `support`
- Source: `hotpotqa`
- Title: Josef Veltjens

Josef "Seppl" Veltjens (2 June 1894 – 6 October 1943) was a German World War I fighter ace credited with 35 victories.

### Document 2

- ID: `hotpotqa_3698_gold_5`
- Role: `support`
- Source: `hotpotqa`
- Title: Hermann Göring

A veteran World War I fighter pilot ace, he was a recipient of the "Pour le Mérite".

**Human judgment:** PASS / FAIL / UNCERTAIN

**Reason:**

---

## Case 26: hotpotqa / contradictory

**Instance ID:** `hotpotqa_5009__contradictory`

**Question:** Carol Kane played the wife of which fictional character on Taxi?

**Gold answer:** Latka Gravas

**Expected abstention:** True

**Evidence:**

### Document 1

- ID: `hotpotqa_5009_gold_0`
- Role: `support`
- Source: `hotpotqa`
- Title: Carol Kane

She appeared on the television series "Taxi" in the early 1980s, as the wife of Latka, the character played by Andy Kaufman, winning two Emmy Awards for her work.

### Document 2

- ID: `hotpotqa_5009_gold_9`
- Role: `support`
- Source: `hotpotqa`
- Title: Latka Gravas

Latka Gravas is a fictional character on the television sitcom "Taxi" portrayed by Andy Kaufman.

### Document 3

- ID: `hotpotqa_5009__contradictory_doc`
- Role: `contradictory`
- Source: `synthetic_controlled_contradiction_v3`
- Title: Independent retrieved record

Question recorded: Carol Kane played the wife of which fictional character on Taxi? Reported answer: Rolling Stone

### Document 4

- ID: `hotpotqa_5009__semantic_noise__0`
- Role: `semantic_distractor`
- Source: `semantic_noise_from_hotpotqa`
- Title: Bo Brady

Bo Brady is a fictional character on the NBC soap opera, "Days of Our Lives", the youngest of the series' Brady family. Created under head-writer Margaret DePriest, the role was originated by Peter Reckell on May 3, 1983. Reckell left the show alongside Kristian Alfonso who played Bo's wife Hope Williams Brady on April 20, 1987. Reckell returned from April 19, 1990, to January 17, 1992, when Robert Kelker-Kelly stepped into the role from March 13, 1992, to July 24, 1995. Reckell returned to portray Bo on August 1, 1995.

### Document 5

- ID: `hotpotqa_5009__semantic_noise__1`
- Role: `semantic_distractor`
- Source: `semantic_noise_from_hotpotqa`
- Title: Trevor Dwyer-Lynch

Trevor Dwyer-Lynch 1968, is a Black British actor, presenter, and stand up comedian. Born and raised in Moss Side and Salford, calls himself a "Mossfordian" trained in Drama and Performing Arts at City College /Arden School of Theatre Manchester in 1990, Dwyer-Lynch has appeared in numerous television and theatre productions, merging both serious roles—such as "Gloucester" in Shakespeare's King Lear— to his best known comedic role in "Coronation Street" as Patrick Tussell the taxi-driver working for Steve McDonald (2002–2005). A dog lover, his 15-stone, Old English Mastiff also appeared with him in an episode, his dog spoiling "Patrick's" attempt to win over love interest Janice Battersby. Lynch achieved one of his wishes working for the Ken Loach in "Looking for Eric", he publicly expresses a desire to work with Directors Shane Meadows, Mike Leigh and Steve McQueen

**Human judgment:** PASS / FAIL / UNCERTAIN

**Reason:**

---

## Case 27: hotpotqa / missing

**Instance ID:** `hotpotqa_494__missing`

**Question:** In which year did this division, where Cleveland Browns placed fourth in 2009, adopt its current name?

**Gold answer:** 2002

**Expected abstention:** True

**Evidence:**

### Document 1

- ID: `hotpotqa_494__semantic_noise__0`
- Role: `semantic_distractor`
- Source: `semantic_noise_from_hotpotqa`
- Title: Minnesota Vikings

The Minnesota Vikings are an American football team based in Minneapolis, Minnesota. The Vikings joined the National Football League (NFL) as an expansion team in 1960, and first took the field for the 1961 season. The team competes in the National Football Conference (NFC) North division; before that, the Vikings were in the NFC Central, and before that they were in the NFL's Western Conference Central Division. The team has played in four Super Bowl games, but have not won one. They were the NFL champions in 1969.

### Document 2

- ID: `hotpotqa_494__semantic_noise__1`
- Role: `semantic_distractor`
- Source: `semantic_noise_from_hotpotqa`
- Title: Miami Marlins

The Miami Marlins are an American professional baseball team based in Miami, Florida. The Marlins compete in Major League Baseball (MLB) as a member club of the National League (NL) East division. Their home park is Marlins Park. Though one of only two MLB franchises to have never won a division title (the other is the Colorado Rockies), the Marlins have won two World Series championships as a wild card team.

### Document 3

- ID: `hotpotqa_494__semantic_noise__2`
- Role: `semantic_distractor`
- Source: `semantic_noise_from_hotpotqa`
- Title: 2017 Minnesota Vikings season

The 2017 season is the Minnesota Vikings' 57th in the National Football League, and the fourth under head coach Mike Zimmer. The Vikings will attempt to make history as the first team to play the Super Bowl on their home field, U.S. Bank Stadium. For the first time since the 2006 season, running back Adrian Peterson will not be on the roster.

### Document 4

- ID: `hotpotqa_494__semantic_noise__3`
- Role: `semantic_distractor`
- Source: `semantic_noise_from_hotpotqa`
- Title: 2009 SEC Championship Game

The 2009 SEC Championship Game was played on December 5, 2009, in the Georgia Dome in Atlanta, Georgia, to determine the 2009 football champion of the Southeastern Conference (SEC). The game featured the Florida Gators and the Alabama Crimson Tide. The Crimson Tide was the designated "home team"; this home team, chosen on an alternating basis, was 2–4 in SEC Championship Games. The winner was all but assured to go on to play for a National Championship, in a likely matchup with the Texas Longhorns provided Texas won in the Big 12 Championship Game versus the north division champion Nebraska Cornhuskers. Entering the 2009 contest, the SEC East was 11–6 in SEC Championship games, with the Florida Gators accounting for seven of the eleven victories.

### Document 5

- ID: `hotpotqa_494__semantic_noise__4`
- Role: `semantic_distractor`
- Source: `semantic_noise_from_hotpotqa`
- Title: Super Bowl XXVI

Super Bowl XXVI was an American football game between the National Football Conference (NFC) champion Washington Redskins and the American Football Conference (AFC) champion Buffalo Bills to decide the National Football League (NFL) champion for the 1991 season. The Redskins defeated the Bills by the score of 37–24, becoming the fourth team after the Pittsburgh Steelers, the Oakland Raiders, and the San Francisco 49ers to win three Super Bowls. The Bills became the third team, after the Minnesota Vikings (Super Bowls VIII and IX) and the Denver Broncos (Super Bowls XXI and XXII), to lose back-to-back Super Bowls. The game was played on January 26, 1992, at the Hubert H. Humphrey Metrodome in Minneapolis, Minnesota, the first time the city has played host to a Super Bowl (the city will host Super Bowl LII at U.S. Bank Stadium).

### Document 6

- ID: `hotpotqa_494__semantic_noise__5`
- Role: `semantic_distractor`
- Source: `semantic_noise_from_hotpotqa`
- Title: 2015 Minnesota Vikings season

The 2015 season was the Minnesota Vikings' 55th season in the National Football League and their second under head coach Mike Zimmer. It marked the last season in which the Vikings played their home games at the University of Minnesota's on-campus TCF Bank Stadium, before moving into U.S. Bank Stadium, which is to open in July 2016, located on the site of the now-demolished Hubert H. Humphrey Metrodome. The Vikings improved on their 7–9 mark from last season and clinched a playoff berth for the first time since 2012. They also won their first NFC North title since 2009 with a Week 17 victory at the Packers. As a result, they hosted the Seattle Seahawks in the wild card round of the 2015–16 NFL playoffs, but lost 10–9 after kicker Blair Walsh missed a potential game-winning, 27-yard field goal in the final seconds.

### Document 7

- ID: `hotpotqa_494__semantic_noise__6`
- Role: `semantic_distractor`
- Source: `semantic_noise_from_hotpotqa`
- Title: 2014 Minnesota Vikings season

The Minnesota Vikings season was the franchise's 54th season in the National Football League and the first under head coach Mike Zimmer. It was the first of two seasons in which the Vikings played at the outdoor TCF Bank Stadium on the campus of the University of Minnesota. Construction of U.S. Bank Stadium began on the site of the Hubert H. Humphrey Metrodome, with a target of opening for the 2016 season.

### Document 8

- ID: `hotpotqa_494__semantic_noise__7`
- Role: `semantic_distractor`
- Source: `semantic_noise_from_hotpotqa`
- Title: Big East Conference (1979–2013)

The Big East Conference was a collegiate athletics conference that consisted of as many as 16 universities in the eastern half of the United States from 1979 to 2013.

**Human judgment:** PASS / FAIL / UNCERTAIN

**Reason:**

---

## Case 28: hotpotqa / noisy

**Instance ID:** `hotpotqa_4838__noisy`

**Question:** A relative of the emu is native to which continent?

**Gold answer:** Africa

**Expected abstention:** False

**Evidence:**

### Document 1

- ID: `hotpotqa_4838_gold_4`
- Role: `support`
- Source: `hotpotqa`
- Title: Emu

The emu ("Dromaius novaehollandiae") is the second-largest living bird by height, after its ratite relative, the ostrich.

### Document 2

- ID: `hotpotqa_4838_gold_9`
- Role: `support`
- Source: `hotpotqa`
- Title: Common ostrich

The ostrich or common ostrich ("Struthio camelus") is either one or two species of large flightless birds native to Africa, the only living member(s) of the genus "Struthio", which is in the ratite family.

### Document 3

- ID: `hotpotqa_4838__semantic_noise__0`
- Role: `semantic_distractor`
- Source: `semantic_noise_from_hotpotqa`
- Title: Polar bear

The polar bear ("Ursus maritimus") is a carnivorous bear whose native range lies largely within the Arctic Circle, encompassing the Arctic Ocean, its surrounding seas and surrounding land masses. It is a large bear, approximately the same size as the omnivorous Kodiak bear ("Ursus arctos middendorffi"). A boar (adult male) weighs around 350 – , while a sow (adult female) is about half that size. Although it is the sister species of the brown bear, it has evolved to occupy a narrower ecological niche, with many body characteristics adapted for cold temperatures, for moving across snow, ice and open water, and for hunting seals, which make up most of its diet. Although most polar bears are born on land, they spend most of their time on the sea ice.

### Document 4

- ID: `hotpotqa_4838__semantic_noise__1`
- Role: `semantic_distractor`
- Source: `semantic_noise_from_hotpotqa`
- Title: North Sea

The North Sea is a marginal sea of the Atlantic Ocean located between Great Britain, Scandinavia, Germany, the Netherlands, Belgium, and France. An epeiric (or "shelf") sea on the European continental shelf, it connects to the ocean through the English Channel in the south and the Norwegian Sea in the north. It is more than 970 km long and 580 km wide, with an area of around 570000 km2 .

### Document 5

- ID: `hotpotqa_4838__semantic_noise__2`
- Role: `semantic_distractor`
- Source: `semantic_noise_from_hotpotqa`
- Title: Lord Frederick Cambridge

Lord Frederick Cambridge ("Frederick Charles Edward") (born Prince Frederick of Teck) (24 September 1907 – 15 May 1940) was a descendant of the British Royal Family. He was the younger son of the Adolphus Cambridge, 1st Marquess of Cambridge, formerly the Duke of Teck, and a nephew of Queen Mary, the consort of King George V.

### Document 6

- ID: `hotpotqa_4838__semantic_noise__3`
- Role: `semantic_distractor`
- Source: `semantic_noise_from_hotpotqa`
- Title: Quechuan languages

Quechua , also known as runa simi ("people's language"), is an indigenous language family, with variations spoken by the Quechua peoples, primarily living in the Andes and highlands of South America. Derived from a common ancestral language, it is the most widely spoken language family of indigenous peoples of the Americas, with a total of probably some 8–10 million speakers. Approximately 13% of Peruvians speak Quechua. It is perhaps most widely known for being the main language of the Inca Empire, and was disseminated by the colonizers throughout their reign.

### Document 7

- ID: `hotpotqa_4838__semantic_noise__4`
- Role: `semantic_distractor`
- Source: `semantic_noise_from_hotpotqa`
- Title: American Eskimo Dog

The American Eskimo Dog is a breed of companion dog originating in Germany. The American Eskimo is a member of the Spitz family. The breed's progenitors were German Spitz, but due to anti-German prejudice during the First World War, it was renamed "American Eskimo Dog". Although modern American Eskimos have been exported as German Spitz Gross (or Mittel, depending on the dog's height), the breeds have diverged and the standards are significantly different. In addition to serving as a watchdog and companion, the American Eskimo Dog also achieved a high degree of popularity in the United States in the 1930s and 1940s as a circus performer.

### Document 8

- ID: `hotpotqa_4838__semantic_noise__5`
- Role: `semantic_distractor`
- Source: `semantic_noise_from_hotpotqa`
- Title: Kermode bear

The Kermode bear ("Ursus americanus kermodei"), also known as the "spirit bear" (particularly in British Columbia), is a rare subspecies of the American black bear living in the Central and North Coast regions of British Columbia, Canada. It is the official provincial mammal of British Columbia. It is noted for about one-tenth of its population having white or cream-coloured coats like polar bears. This colour is due to a double recessive gene unique in the subspecies. They are not albinos and not any more related to polar bears or the "blonde" brown bears of Alaska's "ABC Islands" than other members of their species.

### Document 9

- ID: `hotpotqa_4838__semantic_noise__6`
- Role: `semantic_distractor`
- Source: `semantic_noise_from_hotpotqa`
- Title: History of Wales

The history of Wales begins with the arrival of human beings in the region thousands of years ago. Neanderthals lived in what is now Wales, or "Cymru" in Welsh, at least 230,000 years ago, while "Homo sapiens" arrived by about 31,000 BC. However, continuous habitation by modern humans dates from the period after the end of the last ice age around 9000 BC, and Wales has many remains from the Mesolithic, Neolithic, and Bronze Age. During the Iron Age the region, like all of Britain south of the Firth of Forth, was dominated by the Celtic Britons and the Brittonic language. The Romans, who began their conquest of Britain in AD 43, first campaigned in what is now northeast Wales in 48 against the Deceangli, and gained total control of the region with their defeat of the Ordovices in 79.

### Document 10

- ID: `hotpotqa_4838__semantic_noise__7`
- Role: `semantic_distractor`
- Source: `semantic_noise_from_hotpotqa`
- Title: Pomeranian (dog)

The Pomeranian (often known as a Pom or Pom Pom) is a breed of dog of the Spitz type that is named for the Pomerania region in Germany and Poland in Central Europe. Classed as a toy dog breed because of its small size, the Pomeranian is descended from the larger Spitz type dogs, specifically the German Spitz. It has been determined by the Fédération Cynologique Internationale to be part of the German Spitz breed; and in many countries, they are known as the Zwergspitz ("Dwarf-Spitz").

**Human judgment:** PASS / FAIL / UNCERTAIN

**Reason:**

---

## Case 29: hotpotqa / partial

**Instance ID:** `hotpotqa_5901__partial`

**Question:** What year did the CEO of Tata Consultancy Services takeover as Chairman?

**Gold answer:** 2017

**Expected abstention:** True

**Retained ratio:** 0.3524229074889868

**Evidence:**

### Document 1

- ID: `hotpotqa_5901__partial__hotpotqa_5901_gold_1`
- Role: `partial_support`
- Source: `hotpotqa_partial_v3`
- Title: Tata Sons | retained support fragment

Natarajan Chandrasekaran took over as Chairman of Tata Sons on 21 February 2017.

### Document 2

- ID: `hotpotqa_5901__semantic_noise__0`
- Role: `semantic_distractor`
- Source: `semantic_noise_from_hotpotqa`
- Title: Suhel Seth

Suhel Seth (born May 1963 in Calcutta, West Bengal, India) is a managing partner of consultancy firm Counselage India, founded by him in June 2002. He has previously worked at advertising agencies Response, Ogilvy & Mather and Equus (which he co-founded with his younger brother Swapan in March 1996). He also co-founded the marketing consultancy firm Quadra Advisory with ex-Hindustan Lever marketing guru Shunu Sen in 1997. Seth is also an author, columnist, actor, TV pundit and socialite.

### Document 3

- ID: `hotpotqa_5901__semantic_noise__1`
- Role: `semantic_distractor`
- Source: `semantic_noise_from_hotpotqa`
- Title: Steven Gerrard

Steven George Gerrard {'1': ", '2': ", '3': ", '4': "} (born 30 May 1980) is an English professional football coach and former professional footballer who serves as an academy coach at Liverpool. He spent the majority of his playing career as a central midfielder for Liverpool and the England national team, with most of that time spent as club captain. Regarded as one of the greatest midfielders of his generation, Gerrard was awarded the UEFA Club Footballer of the Year award in 2005, and the Ballon d'Or Bronze Award. In 2009, Zinedine Zidane and Pelé said that they considered Gerrard to be the best footballer in the world. A versatile and well-rounded player, highly regarded for his leadership, Gerrard is the only footballer in history to score in an FA Cup Final, a League Cup Final, a UEFA Cup Final and a UEFA Champions League Final, winning on each occasion.

**Human judgment:** PASS / FAIL / UNCERTAIN

**Reason:**

---

## Case 30: hotpotqa / stale

**Instance ID:** `hotpotqa_2715__stale`

**Question:** Which American chain of bakery-café fast casual restaurants sponsored Bill Steers Men's 4-Miler

**Gold answer:** Panera Bread Company

**Expected abstention:** True

**Evidence:**

### Document 1

- ID: `hotpotqa_2715__stale_doc`
- Role: `stale`
- Source: `synthetic_controlled_stale_v3`
- Title: Archived source snapshot (2013)

Snapshot date: 2013-06-30. Question recorded: Which American chain of bakery-café fast casual restaurants sponsored Bill Steers Men's 4-Miler Reported answer in this snapshot: John John Florence

### Document 2

- ID: `hotpotqa_2715__semantic_noise__0`
- Role: `semantic_distractor`
- Source: `semantic_noise_from_hotpotqa`
- Title: McDonald's Canada

McDonald's Canada (French: "Les Restaurants McDonald du Canada Ltée" ) is the Canadian master franchise of the fast-food restaurant chain McDonald's, owned by the American parent McDonald's Corporation. One of Canada's largest fast-food restaurant chains, the franchise sells food items, including hamburgers, chicken, French fries and soft drinks all across the country. McDonald's is known for its high fat and calorie foods, but it also has alternatives such as salads, juices and milk. McDonald's was previously Canada's largest food service operator before being overtaken by Tim Hortons in 2005. The slogans used in Canada are "i'm lovin' it" (in English) and "c'est ça que j'm" (in French).

### Document 3

- ID: `hotpotqa_2715__semantic_noise__1`
- Role: `semantic_distractor`
- Source: `semantic_noise_from_hotpotqa`
- Title: CVS Health

CVS Health (previously CVS Corporation and CVS Caremark Corporation) (stylized as CVSHealth) is an American retail pharmacy and health care company headquartered in Woonsocket, Rhode Island. The company began in 1964 with three partners who grew the venture from a parent company, Mark Steven, Inc., that helped retailers manage their health and beauty aid product lines. The business began as a chain of health and beauty aid stores, but within several years, pharmacies were added. To facilitate growth and expansion, the company joined The Melville Corporation, which managed a string of retail businesses. Following a period of growth in the 1980s and 1990s, CVS Corporation spun off from Melville in 1996, becoming a standalone company trading on the New York Stock Exchange as

### Document 4

- ID: `hotpotqa_2715__semantic_noise__2`
- Role: `semantic_distractor`
- Source: `semantic_noise_from_hotpotqa`
- Title: Long John Silver's

Long John Silver's LLC is an American fast-food restaurant chain that specializes in seafood. The brand's name is derived from the novel "Treasure Island" by Robert Louis Stevenson, in which the pirate "Long John" Silver is one of the main characters.

### Document 5

- ID: `hotpotqa_2715__semantic_noise__3`
- Role: `semantic_distractor`
- Source: `semantic_noise_from_hotpotqa`
- Title: House of Pies

The Original House of Pies is an American restaurant chain, started c. 1965 by Al Lapin Jr., an early franchise system designer also responsible for International House of Pancakes, Copper Penny Coffee Shops, Orange Julius, and others.

### Document 6

- ID: `hotpotqa_2715__semantic_noise__4`
- Role: `semantic_distractor`
- Source: `semantic_noise_from_hotpotqa`
- Title: Big Boy Restaurants

Big Boy Restaurants International, LLC is an American restaurant chain headquartered in Warren, Michigan, in Metro Detroit. Frisch's Big Boy Restaurants is a restaurant chain with its headquarters in Cincinnati, Ohio. The Big Boy name, design aesthetic, and menu were previously licensed to a number of regional franchisees.

### Document 7

- ID: `hotpotqa_2715__semantic_noise__5`
- Role: `semantic_distractor`
- Source: `semantic_noise_from_hotpotqa`
- Title: Tudor's Biscuit World

Tudor's Biscuit World is a restaurant chain based in Huntington, West Virginia, most commonly found in West Virginia. Many West Virginia locations share a building with Gino's Pizza and Spaghetti, although the chain is more extensive than Gino's (which is exclusive to West Virginia), having locations in southern Ohio, eastern Kentucky, and southwestern Virginia. In 2016 a franchise was opened in Panama City, Florida. Tudor's serves biscuits, biscuit sandwiches, homestyle breakfasts and dinners, muffins, and several side dishes. The chain was originally based in Charleston, West Virginia and many of the biscuit sandwiches are named for sports teams of interest in that area, including teams at Marshall University, West Virginia University, and The University of Charleston.

### Document 8

- ID: `hotpotqa_2715__semantic_noise__6`
- Role: `semantic_distractor`
- Source: `semantic_noise_from_hotpotqa`
- Title: Keebler Company

The Keebler Company is the largest cookie and cracker manufacturer in the United States. Founded in 1853, it has produced numerous baked snacks. Keebler has marketed its brands such as Cheez-It (which have the Sunshine Biscuits brand), Chips Deluxe, Club Crackers, E.L. Fudge Cookies, Famous Amos, Fudge Shoppe Cookies, Murray cookies, Austin, Plantation, Vienna Fingers, Town House Crackers, Wheatables, Sandie's Shortbread, Chachos and Zesta Crackers, among others.

### Document 9

- ID: `hotpotqa_2715__semantic_noise__7`
- Role: `semantic_distractor`
- Source: `semantic_noise_from_hotpotqa`
- Title: Gino's Hamburgers

Gino's Hamburgers was a fast-food restaurant chain founded in Baltimore, Maryland, by Baltimore Colts defensive end Gino Marchetti and running back Alan Ameche, along with their close friend Louis Fischer, in 1957. A new group of restaurants under the Gino's name involving some of the principals of the original chain was started in 2010.

**Human judgment:** PASS / FAIL / UNCERTAIN

**Reason:**

---

## Case 31: pubmedqa / clean

**Instance ID:** `pubmedqa_571__clean`

**Question:** Adults with mild intellectual disabilities: can their reading comprehension ability be improved?

**Gold answer:** yes

**Expected abstention:** False

**Evidence:**

### Document 1

- ID: `pubmedqa_571_ctx_0`
- Role: `support`
- Source: `pubmedqa`
- Title: PubMed abstract section: BACKGROUND

Adults with a mild intellectual disability (ID) often show poor decoding and reading comprehension skills. The goal of this study was to investigate the effects of teaching text comprehension strategies to these adults. Specific research goals were to determine (1) the effects of two instruction conditions, i.e. strategy instruction to individuals and strategy instruction in small groups in a reciprocal teaching context; (2) intervention programme effects on specific strategy tests (so-called direct effects), and possible differences between strategies; (3) (long-term) transfer effects of the programme on general reading comprehension ability; and (4) the regression of general text comprehension by the variables of technical reading, IQ, reading comprehension of sentences (RCS), and pretest and posttest scores on the strategies taught.

### Document 2

- ID: `pubmedqa_571_ctx_1`
- Role: `support`
- Source: `pubmedqa`
- Title: PubMed abstract section: METHODS

In total, 38 adults (age range 20-72 years; mean age of 36 years) with ID participated in the study. IQs ranged from 45 to 69 with a mean IQ of 58. The intervention programme involved 15 weekly lessons of 1 h each, taught during 3 months. Blocks of lessons included each of Brown and Palincsar's strategies of summarizing, questioning, clarifying and predicting, as participants read and studied narrative and expository texts.

### Document 3

- ID: `pubmedqa_571_ctx_2`
- Role: `support`
- Source: `pubmedqa`
- Title: PubMed abstract section: RESULTS

Results indicated no significant difference between group and individual instruction conditions. Second, direct programme effects - as determined by posttest-pretest contrasts for strategy tests - were substantial, except for the questioning strategy. Third, even more substantial was the transfer effect to general text comprehension. Moreover, the results on this test were well maintained at a follow-up test. Finally, the variance of general reading comprehension ability was best explained by the test of RCS, and only moderately by the strategies trained.

**Human judgment:** PASS / FAIL / UNCERTAIN

**Reason:**

---

## Case 32: pubmedqa / contradictory

**Instance ID:** `pubmedqa_712__contradictory`

**Question:** Should all human immunodeficiency virus-infected patients with end-stage renal disease be excluded from transplantation?

**Gold answer:** no

**Expected abstention:** True

**Evidence:**

### Document 1

- ID: `pubmedqa_712_ctx_0`
- Role: `support`
- Source: `pubmedqa`
- Title: PubMed abstract section: BACKGROUND

Human immunodeficiency virus (HIV)-infected patients have generally been excluded from transplantation. Recent advances in the management and prognosis of these patients suggest that this policy should be reevaluated.

### Document 2

- ID: `pubmedqa_712_ctx_1`
- Role: `support`
- Source: `pubmedqa`
- Title: PubMed abstract section: METHODS

To explore the current views of U.S. transplant centers toward transplanting asymptomatic HIV-infected patients with end-stage renal disease, a written survey was mailed to the directors of transplantation at all 248 renal transplant centers in the United States.

### Document 3

- ID: `pubmedqa_712_ctx_2`
- Role: `support`
- Source: `pubmedqa`
- Title: PubMed abstract section: RESULTS

All 148 responding centers said they require HIV testing of prospective kidney recipients, and 84% of these centers would not transplant an individual who refuses HIV testing. The vast majority of responding centers would not transplant a kidney from a cadaveric (88%) or a living donor (91%) into an asymptomatic HIV-infected patient who is otherwise a good candidate for transplantation. Among the few centers that would consider transplanting an HIV-infected patient, not a single center had performed such a transplant in the year prior to the survey. Most centers fear that transplantation in the face of HIV infection would be harmful to the individual, and some believe that it would be a waste of precious organs.

### Document 4

- ID: `pubmedqa_712__contradictory_doc`
- Role: `contradictory`
- Source: `synthetic_controlled_contradiction_v3`
- Title: Independent retrieved record

Question recorded: Should all human immunodeficiency virus-infected patients with end-stage renal disease be excluded from transplantation? Reported answer: yes

### Document 5

- ID: `pubmedqa_712__semantic_noise__0`
- Role: `semantic_distractor`
- Source: `semantic_noise_from_pubmedqa`
- Title: PubMed abstract section: PURPOSE

A higher prevalence of cardiovascular risk factors (CRFs) in HIV-infected patients, together with chronic infection and treatments, has resulted in an increased risk of silent myocardial ischaemia (SMI). The objective of this study was to evaluate whether myocardial SPECT should be used for screening HIV-infected patients with no clinical symptoms of coronary artery disease.

### Document 6

- ID: `pubmedqa_712__semantic_noise__1`
- Role: `semantic_distractor`
- Source: `semantic_noise_from_pubmedqa`
- Title: PubMed abstract section: MAIN BODY

The introduction and widespread use of ART have drastically changed the natural history of HIV/AIDS, but exposure to ART leads to serious medication-related adverse effects mainly explained by mitochondrial toxicities, and the situation will get worse in the near future. Indeed, ART is associated with an increased risk of developing cardiovascular disease, lipodystrophy, prediabetes and overt diabetes, insulin resistance and hyperlactatemia/lactic acidosis. The prevalence of these disorders is already high in SSA, and the situation will be exacerbated by the implementation of the new WHO recommendations. Most SSA countries are characterized by (extreme) poverty, very weak health systems, inadequate and low quality of health services, inaccessibility to existing health facilities, lack of (qualified) health personnel, lack of adequate equipment, inaccessibility and unaffordability of medicines, and heavy workload in a context of a double burden of disease. Additionally, there is dearth of data on the incidence and predictive factors of ART-related adverse effects in SSA, to anticipate on strategies that should be put in place to prevent the occurrence of these conditions or properly ...

**Human judgment:** PASS / FAIL / UNCERTAIN

**Reason:**

---

## Case 33: pubmedqa / missing

**Instance ID:** `pubmedqa_349__missing`

**Question:** Does automatic transmission improve driving behavior in older drivers?

**Gold answer:** yes

**Expected abstention:** True

**Evidence:**

### Document 1

- ID: `pubmedqa_349__semantic_noise__0`
- Role: `semantic_distractor`
- Source: `semantic_noise_from_pubmedqa`
- Title: PubMed abstract section: DESIGN

Follow up study of mortality in relation to employment grade and car ownership over 25 years.

### Document 2

- ID: `pubmedqa_349__semantic_noise__1`
- Role: `semantic_distractor`
- Source: `semantic_noise_from_pubmedqa`
- Title: PubMed abstract section: RESULTS

Both young and older adults were able to use the target strategies on the WM task and showed gains in WM performance after training. The age-related WM deficit was not greatly affected, however, and the training gains did not transfer to the other cognitive tasks. In fact, participants attempted to adapt the trained strategies for a paired-associate recall task, but the increased strategy use did not benefit their performance.

### Document 3

- ID: `pubmedqa_349__semantic_noise__2`
- Role: `semantic_distractor`
- Source: `semantic_noise_from_pubmedqa`
- Title: PubMed abstract section: METHODS

The 56 participants were originally recruited for a prospective study on driving and community re-integration post-stroke; the study population consisted of moderately impaired stroke survivors without severe communication disorders who had been referred for a driving assessment. The driving records of the 56 participants for the 5 years before study entry and the 1-year study period were acquired with written consent from the Ministry of Transportation of Ontario (MTO), Canada. Self-reports of collisions and convictions were acquired via a semistructured interview and then compared with the MTO records.

### Document 4

- ID: `pubmedqa_349__semantic_noise__3`
- Role: `semantic_distractor`
- Source: `semantic_noise_from_pubmedqa`
- Title: PubMed abstract section: PARTICIPANTS

Individuals aged 55 and older without dementia.

### Document 5

- ID: `pubmedqa_349__semantic_noise__4`
- Role: `semantic_distractor`
- Source: `semantic_noise_from_pubmedqa`
- Title: PubMed abstract section: METHODS

Participants in the training group (older adults: n = 39; young adults: n = 41) were taught about various verbal encoding strategies and their differential effectiveness and were trained to use interactive imagery and sentence generation on a list-learning task. Participants in the control group (older: n = 37; young: n = 38) completed an equally engaging filler task. All participants completed a pre- and post-training reading span task, which included self-reported strategy use, as well as two transfer tasks that differed in the affordance to use the trained strategies - a paired-associate recall task and the self-ordered pointing task.

### Document 6

- ID: `pubmedqa_349__semantic_noise__5`
- Role: `semantic_distractor`
- Source: `semantic_noise_from_pubmedqa`
- Title: PubMed abstract section: OBJECTIVE

ESC (Electronic Stability Control) is a crash avoidance technology that reduces the likelihood of collisions involving loss of control. Although past and emerging research indicates that ESC is effective in reducing collision rates and saving lives, and its inclusion in all vehicle platforms is encouraged, drivers may demonstrate behavioral adaptation or an overreliance on ESC that could offset or reduce its overall effectiveness. The main objective of the present study was to determine whether behavioral adaptation to ESC is likely to occur upon the widespread introduction of ESC into the Canadian vehicle fleet. Secondary objectives were to confirm the results of a previous ESC public survey and to generate a baseline measure for the future assessment of planned and ongoing ESC promotional activities in Canada.

### Document 7

- ID: `pubmedqa_349__semantic_noise__6`
- Role: `semantic_distractor`
- Source: `semantic_noise_from_pubmedqa`
- Title: PubMed abstract section: BACKGROUND

Older adults typically perform worse on measures of working memory (WM) than do young adults; however, age-related differences in WM performance might be reduced if older adults use effective encoding strategies.

### Document 8

- ID: `pubmedqa_349__semantic_noise__7`
- Role: `semantic_distractor`
- Source: `semantic_noise_from_pubmedqa`
- Title: PubMed abstract section: RESULTS

Forty-three participants completed the study. For 7 (13.5%) the MTO records did not match the self-reports regarding collision involvement, and for 9 (17.3%) the MTO records did not match self-reports regarding driving convictions. The kappa coefficient for the correlation between MTO records and self-reports was 0.52 for collisions and 0.47 for convictions (both in the moderate range of agreement). When both sources of data were consulted, up to 56 percent more accidents and up to 46 percent more convictions were identified in the study population in the 5 years before study entry compared to when either source was used alone.

**Human judgment:** PASS / FAIL / UNCERTAIN

**Reason:**

---

## Case 34: pubmedqa / noisy

**Instance ID:** `pubmedqa_901__noisy`

**Question:** Laparoscopic myomectomy: do size, number, and location of the myomas form limiting factors for laparoscopic myomectomy?

**Gold answer:** no

**Expected abstention:** False

**Evidence:**

### Document 1

- ID: `pubmedqa_901_ctx_0`
- Role: `support`
- Source: `pubmedqa`
- Title: PubMed abstract section: STUDY OBJECTIVE

To assess whether it is possible for an experienced laparoscopic surgeon to perform efficient laparoscopic myomectomy regardless of the size, number, and location of the myomas.

### Document 2

- ID: `pubmedqa_901_ctx_1`
- Role: `support`
- Source: `pubmedqa`
- Title: PubMed abstract section: DESIGN

Prospective observational study (Canadian Task Force classification II-1).

### Document 3

- ID: `pubmedqa_901_ctx_2`
- Role: `support`
- Source: `pubmedqa`
- Title: PubMed abstract section: SETTING

Tertiary endoscopy center.

### Document 4

- ID: `pubmedqa_901_ctx_3`
- Role: `support`
- Source: `pubmedqa`
- Title: PubMed abstract section: PATIENTS

A total of 505 healthy nonpregnant women with symptomatic myomas underwent laparoscopic myomectomy at our center. No exclusion criteria were based on the size, number, or location of myomas.

### Document 5

- ID: `pubmedqa_901_ctx_4`
- Role: `support`
- Source: `pubmedqa`
- Title: PubMed abstract section: INTERVENTIONS

Laparoscopic myomectomy and modifications of the technique: enucleation of the myoma by morcellation while it is still attached to the uterus with and without earlier devascularization.

### Document 6

- ID: `pubmedqa_901_ctx_5`
- Role: `support`
- Source: `pubmedqa`
- Title: PubMed abstract section: MEASUREMENTS AND MAIN RESULTS

In all, 912 myomas were removed in these 505 patients laparoscopically. The mean number of myomas removed was 1.85 +/- 5.706 (95% CI 1.72-1.98). In all, 184 (36.4%) patients had multiple myomectomy. The mean size of the myomas removed was 5.86 +/- 3.300 cm in largest diameter (95% CI 5.56-6.16 cm). The mean weight of the myomas removed was 227.74 +/- 325.801 g (95% CI 198.03-257.45 g) and median was 100 g. The median operating time was 60 minutes (range 30-270 minutes). The median blood loss was 90 mL (range 40-2000 mL). Three comparisons were performed on the basis of size of the myomas (<10 cm and>or=10 cm in largest diameter), number of myomas removed (<or=4 and>or=5 myomas), and the technique (enucleation of the myomas by morcellation while the myoma is still attached to the uterus and the conventional technique). In all these comparisons, although the mean blood loss, duration of surgery, and hospital stay were greater in the groups in which larger myomas or more myomas were removed or the modified technique was performed as compared with their corresponding study group, the weight and size of removed myomas were also proportionately larger in these groups. Two patients were g ...

### Document 7

- ID: `pubmedqa_901__semantic_noise__0`
- Role: `semantic_distractor`
- Source: `semantic_noise_from_pubmedqa`
- Title: PubMed abstract section: RESULTS

The patients in the GS group were older (median age, 63 vs 53 years; p = 0.01). In all, 31 LS patients (65%), as compared with 44 GS patients (36%), had successful laparoscopic treatment (p = 0.001). The operating time was the same (median, 70 min). The proportion of patients with postoperative complications was similar in the two groups (37% in the GS vs 31% in the LS group; p = 0.6). The median postoperative hospital stay (3 vs 5 days; p<0.01) was shorter in the LS group. On logistic regression analysis, significant predictors of a successful laparoscopic operation included LS group (p<0.01) and age (p = 0). Predictors of prolonged length of hospital stay were age (p<0.01) and comorbidity score (p<0.01), with LS group status not a significant factor (p = 0.21).

### Document 8

- ID: `pubmedqa_901__semantic_noise__1`
- Role: `semantic_distractor`
- Source: `semantic_noise_from_pubmedqa`
- Title: PubMed abstract section: STUDY DESIGN

Electrical uterine myography (EUM) was measured prospectively on 87 women, gestational age less than 35 weeks. The period between contractions, power of contraction peaks and movement of center of electrical activity (RMS), was used to develop an index score (1-5) for prediction of preterm delivery (PTD) within 14 days of the test. The score was compared with fetal fibronectin (fFN) and cervical length (CL).

### Document 9

- ID: `pubmedqa_901__semantic_noise__2`
- Role: `semantic_distractor`
- Source: `semantic_noise_from_pubmedqa`
- Title: PubMed abstract section: METHODS

A retrospective analysis was performed from a single institution, including 2,301 patients undergoing LAGB with HHR from July 1, 2007 to December 31, 2011. Independent variables were number and location of sutures. Data collected included demographics, operating room (OR) time, length of stay (LOS), follow-up time, postoperative BMI/%EWL, and rates of readmission/reoperation. Statistical analyses included ANOVA and Chi squared tests. Kaplan-Meier, log-rank, and Cox regression tests were used for follow-up data and reoperation rates, in order to account for differential length of follow-up and confounding variables.

### Document 10

- ID: `pubmedqa_901__semantic_noise__3`
- Role: `semantic_distractor`
- Source: `semantic_noise_from_pubmedqa`
- Title: PubMed abstract section: RESULTS

Sixteen women developed adverse pregnancy outcome. In these women, right uterine artery PI and RI were significantly higher than in women with normal obstetrical outcome. Spiral artery PI and RI values were also higher, but the difference was not statistically significant. GS-CRL difference, GS/CRL ratio, and yolk sac diameters were significantly lower in this group.

### Document 11

- ID: `pubmedqa_901__semantic_noise__4`
- Role: `semantic_distractor`
- Source: `semantic_noise_from_pubmedqa`
- Title: PubMed abstract section: RESULTS

Using the GBSR, data from 5.400 LSGs were considered for analysis. Staple line leak rate decreased during the study period from 6.5 to 1.4 %. Male gender, higher BMI, concomitant sleep apnea, conversion to laparotomy, longer operation time, use of both buttresses and oversewing, and the occurrence of intraoperative complications were associated with a significantly higher leakage rate. On multivariate analysis, operation time and year of procedure only had a significant impact on staple line leak rate.

### Document 12

- ID: `pubmedqa_901__semantic_noise__5`
- Role: `semantic_distractor`
- Source: `semantic_noise_from_pubmedqa`
- Title: PubMed abstract section: RESULTS

There were 36 torsions in 34 children. Seventeen underwent detorsion with or without ovarian cystectomy, and 19 had oophorectomy (mean age 10 years in both groups). Torsion was suspected preoperatively in 94% of the detorsion cases and in 47% of the oophorectomy patients. Median time from presentation to surgery was significantly lower in the detorsion than the oophorectomy group (median 14 v 27 hours; P =.04). Postoperative complications and length of stay were similar between the 2 groups. Despite the ovary being judged intraoperatively as moderately to severely ischemic in 53% of the detorsion cases, follow-up sonogram or ovarian biopsy available in 14 of the 17 cases showed normal ovary with follicular development in each case.

**Human judgment:** PASS / FAIL / UNCERTAIN

**Reason:**

---

## Case 35: pubmedqa / partial

**Instance ID:** `pubmedqa_136__partial`

**Question:** Can transcranial direct current stimulation be useful in differentiating unresponsive wakefulness syndrome from minimally conscious state patients?

**Gold answer:** yes

**Expected abstention:** True

**Retained ratio:** 0.11309062742060419

**Evidence:**

### Document 1

- ID: `pubmedqa_136__partial__pubmedqa_136_ctx_2`
- Role: `partial_support`
- Source: `pubmedqa_partial_v3`
- Title: PubMed abstract section: RESULT | retained abstract section

a-tDCS was able to boost cortical connectivity and excitability in all HC, MCS, and to unmask such excitability/connectivity in some UWS patients.

### Document 2

- ID: `pubmedqa_136__semantic_noise__0`
- Role: `semantic_distractor`
- Source: `semantic_noise_from_pubmedqa`
- Title: PubMed abstract section: OBJECTIVE

To determine the potential prognostic value of using functional magnetic resonance imaging (fMRI) to identify patients with disorders of consciousness, who show potential for recovery.

### Document 3

- ID: `pubmedqa_136__semantic_noise__1`
- Role: `semantic_distractor`
- Source: `semantic_noise_from_pubmedqa`
- Title: PubMed abstract section: OBJECTIVE

To investigate the ability of a bedside swallowing assessment to reliably exclude aspiration following acute stroke.

**Human judgment:** PASS / FAIL / UNCERTAIN

**Reason:**

---

## Case 36: pubmedqa / stale

**Instance ID:** `pubmedqa_952__stale`

**Question:** Is solitary kidney really more resistant to ischemia?

**Gold answer:** yes

**Expected abstention:** True

**Evidence:**

### Document 1

- ID: `pubmedqa_952__stale_doc`
- Role: `stale`
- Source: `synthetic_controlled_stale_v3`
- Title: Archived source snapshot (2017)

Snapshot date: 2017-06-30. Question recorded: Is solitary kidney really more resistant to ischemia? Reported answer in this snapshot: no

### Document 2

- ID: `pubmedqa_952__semantic_noise__0`
- Role: `semantic_distractor`
- Source: `semantic_noise_from_pubmedqa`
- Title: PubMed abstract section: INTRODUCTION

The solitary kidney (SK) is currently debated in the literature, as living kidney donation is extensively used and the diagnosis of congenital SK is frequent. Tubulointerstitial lesions associated with adaptive phenomena may occur early within the SK.

### Document 3

- ID: `pubmedqa_952__semantic_noise__1`
- Role: `semantic_distractor`
- Source: `semantic_noise_from_pubmedqa`
- Title: PubMed abstract section: METHODS

From July 2004 to June 2005, 18 patients underwent LPN with warm ischemia time>30 min. Kidney damage markers (daily proteinuria and tubular enzymes) and renal function (serum creatinine, cystatin C, and creatinine clearances) were assessed on postoperative days 1 and 5 and at 12 mo. Glomerular filtration rate (GFR) was evaluated before surgery and at 3 mo. Renal scintigraphy was performed before the procedure, at 5 d and at 3 and 12 mo postoperatively. Statistical analysis was performed using the Student t test and logistic regression analysis.

### Document 4

- ID: `pubmedqa_952__semantic_noise__2`
- Role: `semantic_distractor`
- Source: `semantic_noise_from_pubmedqa`
- Title: PubMed abstract section: OBJECTIVE

To evaluate renal damage and impairment of renal function 1 yr after laparoscopic partial nephrectomy (LPN) with warm ischemia>30 min.

### Document 5

- ID: `pubmedqa_952__semantic_noise__3`
- Role: `semantic_distractor`
- Source: `semantic_noise_from_pubmedqa`
- Title: PubMed abstract section: METHODS

A cross-sectional study of 37 patients with SK included 18 patients-acquired SK (mean age 56.44 ± 12.20 years, interval from nephrectomy 10.94 ± 9.37 years), 19 patients-congenital SK (mean age 41.52 ± 10.54 years). Urinary NAG, urinary alpha-1-microglobulin, albuminuria, eGFR (CKD-EPI equation) were measured.

### Document 6

- ID: `pubmedqa_952__semantic_noise__4`
- Role: `semantic_distractor`
- Source: `semantic_noise_from_pubmedqa`
- Title: PubMed abstract section: RESULTS

In terms of kidney damage and renal function markers, the statistical analysis demonstrated that at 1 yr there was complete return to the normal range and no statistical difference between the values at the various time points. The GFR was not significantly different before and 3 mo after surgery. In terms of scintigraphy of the operated kidney, the values were 48.35+/-3.82% (40-50%) before the procedure, 36.88+/-8.42 (16-50%) on postoperative day 5 (p=0.0001), 40.56+/-8.96 (20-50%) at 3 mo (p=0.003), and 42.8+/-7.2% (20-50%) 1 yr after surgery (p=0.001).

### Document 7

- ID: `pubmedqa_952__semantic_noise__5`
- Role: `semantic_distractor`
- Source: `semantic_noise_from_pubmedqa`
- Title: PubMed abstract section: MATERIAL

Temperature was monitored using the Thermobouton probe during preservation of pig kidneys, in the same conditions used with human grafts. The probe recorded the temperature level every 10 minutes during four days. We compared the results found with the new storage can with results obtained in the same conditions with the storage can formerly used by our team. We also studied the best position of the probe for temperature monitoring and the influence of the amount of ice within the transport pack on the temperature level. We then monitored the temperature during the conservation of actual human kidney grafts harvested at our institution from August 2007 to May 2008.

### Document 8

- ID: `pubmedqa_952__semantic_noise__6`
- Role: `semantic_distractor`
- Source: `semantic_noise_from_pubmedqa`
- Title: PubMed abstract section: RESULTS

In the IR group, total coronary flow (TCF=LAD+Cx+RCA blood-flow) decreased precipitously and significantly from baseline (113±41 ml min"1) during IR (p<0.05), with the lowest value observed at 60 min of reperfusion (-37.1%, p<0.003). Baseline cTn (0.08±0.02 ng ml(-1)) increased during IR and peaked at 45 min of reperfusion (+138%, p<0.001). Baseline IL-6 (9.2±2.17 pg ml(-1)) increased during IR and peaked at 60 min of reperfusion (+228%, p<0.0001). Significant LVP drop at 5 min of ischemia (p<0.05) was followed by a slow return to baseline at 45 min of ischemia. A second LVP drop occurred at reperfusion (p<0.05) and persisted. Conversely, RVP increased throughout ischemia (p<0.05) and returned toward baseline during reperfusion. Coronary blood flow and hemodynamic profile remained unchanged in the control group. IL-10 and TNF-A remained below the measurable range for both the groups.

### Document 9

- ID: `pubmedqa_952__semantic_noise__7`
- Role: `semantic_distractor`
- Source: `semantic_noise_from_pubmedqa`
- Title: PubMed abstract section: RESULTS

Fifty-seven consecutive patients were included. The average age was 64.4 ± 10.7, 73% of the patients were males, and nearly half of the patients were known to have ischemic heart disease. Two of the patients were excluded due to technical difficulty. No signs of ischemia were recorded in 25 (45.4%). Among the patients with established ischemia on DSE, 12 (22%) had mild ischemia, 13 (23.6%) had moderate and 5 (9%) had severe ischemia. Angiography was performed in 13 (26%) of the patients, of which 7 had PCI and one was referred to bypass surgery. None of the patients had elevated cTnI 18-24 hours after the DSE.

**Human judgment:** PASS / FAIL / UNCERTAIN

**Reason:**

---

## Case 37: tatqa / clean

**Instance ID:** `tatqa_53_0__clean`

**Question:** What is included among non-financial assets and liabilities that are not required to be measured at fair value on a recurring basis?

**Gold answer:** inventories, net property and equipment, goodwill, intangible assets and asset retirement obligations.

**Expected abstention:** False

**Evidence:**

### Document 1

- ID: `tatqa_53_0_gold_0`
- Role: `support`
- Source: `tatqa`
- Title: TAT-QA document 53, question 0

Paragraph evidence: The table below shows the carrying amounts and estimated fair values of our debt, excluding lease liabilities: (1) Includes borrowings denominated in currencies other than US Dollars. (2) At December 31, 2019, the carrying amount and estimated fair value of debt exclude lease liabilities. In addition to the table above, the Company remeasures amounts related to certain equity compensation that are carried at fair value on a recurring basis in the Consolidated Financial Statements or for which a fair value measurement was required. Refer to Note 21, “Stockholders’ Deficit,” of the Notes to Consolidated Financial Statements for share-based compensation in the Notes to Consolidated Financial Statements. Included among our non-financial assets and liabilities that are not required to be measured at fair value on a recurring basis are inventories, net property and equipment, goodwill, intangible assets and asset retirement obligations. Financial table: uid: 529f67ed9786a369a2277717e640dfec table: December 31, 2019 December 31, 2018 (In millions) Carrying Amount Fair Value Carrying Amount Fair Value Term Loan A Facility due July 2022 $ 474.6 $ 474.6 $ — $ — Term Loan  ...

**Human judgment:** PASS / FAIL / UNCERTAIN

**Reason:**

---

## Case 38: tatqa / contradictory

**Instance ID:** `tatqa_67_5__contradictory`

**Question:** What is the average Gross margin (as percentage of net revenues)?

**Gold answer:** 39.3

**Expected abstention:** True

**Evidence:**

### Document 1

- ID: `tatqa_67_5_gold_0`
- Role: `support`
- Source: `tatqa`
- Title: TAT-QA document 67, question 5

Paragraph evidence: In 2019, gross margin decreased by 130 basis points to 38.7% from 40.0% in the full year 2018 mainly due to normal price pressure and increased unsaturation charges, partially offset by improved manufacturing efficiencies, better product mix, and favorable currency effects, net of hedging. Unused capacity charges in 2019 were $65 million, impacting full year gross margin by 70 basis points. In 2018, gross margin improved by 80 basis points to 40.0% from 39.2% in the full year 2017 benefiting from manufacturing efficiencies and better product mix, partially offset by normal price pressure and unfavorable currency effects, net of hedging. In 2018 unused capacity charges were negligible. Financial table: uid: e65078d0c208393b185d7519fe2f78d5 table: Year Ended December 31, Year Ended December 31, Year Ended December 31, Variation Variation 2019 2018 2017 2019 vs 2018 2018 vs 2017 (In millions) (In millions) (In millions) Cost of sales $(5,860) $(5,803) $(5,075) 1.0% (14.3)% Gross profit $3,696 $3,861 $3,272 (4.3)% 18.0% Gross margin (as percentage of net revenues) 38.7% 40.0% 39.2% -130 bps +80 bps

### Document 2

- ID: `tatqa_67_5__contradictory_doc`
- Role: `contradictory`
- Source: `synthetic_controlled_contradiction_v3`
- Title: Independent retrieved record

Question recorded: What is the average Gross margin (as percentage of net revenues)? Reported answer: 15.4

### Document 3

- ID: `tatqa_67_5__semantic_noise__0`
- Role: `semantic_distractor`
- Source: `semantic_noise_from_tatqa`
- Title: TAT-QA document 222, question 4

Paragraph evidence: Gross profit The recent shift in our revenue mix toward cloud arrangements has resulted in slower total gross profit growth as our cloud business continues to grow and scale. Revenue from cloud arrangements is generally recognized over the service period, while revenue from term and perpetual license arrangements is generally recognized upfront when the license rights become effective. Gross profit The increase in total gross profit in 2019 was primarily due to increases in cloud and maintenance revenue. Gross profit percent The decrease in cloud gross profit percent in 2019 was driven by an increase in costs as we accelerated our investments in cloud infrastructure and service delivery to support future growth. The decrease in consulting gross profit percent in 2019 was driven by a decrease in billable hours as consulting resources were transitioning to new projects after completing a large project and an increase in consulting resource availability as we continue growing and leveraging our partner network. Financial table: uid: b7ca9197512c59935aef8cfee1a33000 table: (Dollars in thousands) 2019 2018 Change Software license $275,792 99% $282,950 98% $(7,158) (3 ...

### Document 4

- ID: `tatqa_67_5__semantic_noise__1`
- Role: `semantic_distractor`
- Source: `semantic_noise_from_tatqa`
- Title: TAT-QA document 92, question 5

Paragraph evidence: NOTES TO CONSOLIDATED FINANCIAL STATEMENTS (in thousands, except for share and per share data) NOTE 21 — Quarterly Financial Data Quarterly Results of Operations (Unaudited) Financial table: uid: 43d14c2668f66a09b23eeea467f4f1d3 table: First Second Third Fourth 2019 Net sales $117,625 $120,684 $115,651 $115,040 Gross margin $40,615 $41,204 $37,057 $38,700 Operating earnings $14,218 $17,083 $10,124 $12,391 Net earnings $11,419 $11,943 $2,722 $10,062 Basic earnings per share $0.35 $0.36 $0.08 $0.31 Diluted earnings per share $0.34 $0.36 $0.08 $0.31 2018 Net sales $113,530 $118,021 $118,859 $120,073 Gross margin $38,433 $41,813 $42,082 $42,645 Operating earnings $13,359 $14,544 $16,118 $17,017 Net earnings $ 11,54 $7,209 $10,211 $17,564 Basic earnings per share $0.35 $0.22 $0.31 $0.53 Diluted earnings per share $0.34 $0.21 $0.30 $0.52

**Human judgment:** PASS / FAIL / UNCERTAIN

**Reason:**

---

## Case 39: tatqa / missing

**Instance ID:** `tatqa_185_1__missing`

**Question:** What was the amount of Rent and other deposits in 2018?

**Gold answer:** 5,687

**Expected abstention:** True

**Evidence:**

### Document 1

- ID: `tatqa_185_1__semantic_noise__0`
- Role: `semantic_distractor`
- Source: `semantic_noise_from_tatqa`
- Title: TAT-QA document 197, question 5

Paragraph evidence: The table below details the percentage of the number of investment properties subject to internal and external valuations during the current and comparable reporting periods The Group also obtained external valuations on 31 freehold investment properties acquired during the year ended 30 June 2019 (year ended 30 June 2018: 19 freehold investment properties). These external valuations provide the basis of the Directors’ valuations applied to these properties at 30 June 2019 and 30 June 2018. Including these valuations, 51% of freehold investment properties were subject to external valuations during the year (year ended 30 June 2018: 43% of freehold investment properties). Financial table: uid: 78dbdf3d45453c264f21590f247620c8 table: External valuation % Internal valuation % Year ended 30 June 2019 Leasehold 23% 77% Freehold 38% 62% Year ended 30 June 2018 Leasehold 60% 40% Freehold 27% 73%

### Document 2

- ID: `tatqa_185_1__semantic_noise__1`
- Role: `semantic_distractor`
- Source: `semantic_noise_from_tatqa`
- Title: TAT-QA document 45, question 2

Paragraph evidence: The following table sets forth, for the periods indicated, our working capital: Working Capital consists of current assets net of current liabilities. Working capital decreased $0.4 million to $12.3 million at December 31, 2019 compared with $12.7 million at December 31, 2018. The decrease was primarily a result of an increase of cash, accounts receivable, and inventory offset by an increase in accounts payable, accrued expenses and current operating lease liabilities. We normally carry three to four weeks of finished goods inventory. The average duration of our accounts receivable is approximately 25 days. For the year ended December 31, 2019 our capital resources consisted of primarily $9.5 million cash on hand and $33.0 million available under our credit facilities, net of $2.0 million reserved for two letters of credit. For the year ended December 31, 2018, our capital resources consisted primarily of $7.5 million cash on hand and $30.0 million available under our credit facilities. The Credit Facilities will mature in May 2024. We borrowed $72.3 million under our credit facilities during 2019, of which $18.5 million was repaid prior to the end of the year.  ...

### Document 3

- ID: `tatqa_185_1__semantic_noise__2`
- Role: `semantic_distractor`
- Source: `semantic_noise_from_tatqa`
- Title: TAT-QA document 45, question 1

Paragraph evidence: The following table sets forth, for the periods indicated, our working capital: Working Capital consists of current assets net of current liabilities. Working capital decreased $0.4 million to $12.3 million at December 31, 2019 compared with $12.7 million at December 31, 2018. The decrease was primarily a result of an increase of cash, accounts receivable, and inventory offset by an increase in accounts payable, accrued expenses and current operating lease liabilities. We normally carry three to four weeks of finished goods inventory. The average duration of our accounts receivable is approximately 25 days. For the year ended December 31, 2019 our capital resources consisted of primarily $9.5 million cash on hand and $33.0 million available under our credit facilities, net of $2.0 million reserved for two letters of credit. For the year ended December 31, 2018, our capital resources consisted primarily of $7.5 million cash on hand and $30.0 million available under our credit facilities. The Credit Facilities will mature in May 2024. We borrowed $72.3 million under our credit facilities during 2019, of which $18.5 million was repaid prior to the end of the year.  ...

### Document 4

- ID: `tatqa_185_1__semantic_noise__3`
- Role: `semantic_distractor`
- Source: `semantic_noise_from_tatqa`
- Title: TAT-QA document 140, question 5

Paragraph evidence: 4. Other Current Assets Other current assets consist of (in thousands): Financial table: uid: 814795f164b6a3e1d39d22c3814cc288 table: December 31, 2019 2018 Indemnification receivable from SSL for pre-closing taxes (see Note 13) $598 $2,410 Due from affiliates 186 161 Prepaid expenses 164 151 Other 374 510 $1,322 $3,232

### Document 5

- ID: `tatqa_185_1__semantic_noise__4`
- Role: `semantic_distractor`
- Source: `semantic_noise_from_tatqa`
- Title: TAT-QA document 140, question 3

Paragraph evidence: 4. Other Current Assets Other current assets consist of (in thousands): Financial table: uid: 814795f164b6a3e1d39d22c3814cc288 table: December 31, 2019 2018 Indemnification receivable from SSL for pre-closing taxes (see Note 13) $598 $2,410 Due from affiliates 186 161 Prepaid expenses 164 151 Other 374 510 $1,322 $3,232

### Document 6

- ID: `tatqa_185_1__semantic_noise__5`
- Role: `semantic_distractor`
- Source: `semantic_noise_from_tatqa`
- Title: TAT-QA document 169, question 5

Paragraph evidence: The following table sets forth a summary of our cash flows for the periods indicated (in thousands): Our cash flows from operating activities are significantly influenced by our growth, ability to maintain our contractual billing and collection terms, and our investments in headcount and infrastructure to support anticipated growth. Given the seasonality and continued growth of our business, our cash flows from operations will vary from period to period. Cash provided by operating activities was $115.5 million in 2019, compared to $90.3 million in 2018. The increase in operating cash flow was primarily due to improved profitability, improved collections, and other working capital changes in 2019 when compared to 2018. Financial table: uid: 4b528eb35807a61dcad7b7f9c3b994a2 table: Year Ended December 31, 2019 2018 2017 Net cash provided by operating activities $115,549 $90,253 $67,510 Net cash used in investing activities (97,727) (20,876) (36,666) Net cash provided by (used in) financing activities 14,775 (278,016) 276,852

### Document 7

- ID: `tatqa_185_1__semantic_noise__6`
- Role: `semantic_distractor`
- Source: `semantic_noise_from_tatqa`
- Title: TAT-QA document 213, question 4

Paragraph evidence: Note 8. Property, Plant and Equipment, net Property, plant and equipment, net as of December 31, 2019 and 2018 consisted of the following: (1) Useful lives for leasehold and building improvements represent the term of the lease or the estimated life of the related improvements, whichever is shorter. Depreciation expense from continuing operations was $12,548 and $12,643 for the years ended December 31, 2019 and 2018, respectively, of which $9,028 and $9,189, respectively, related to internal use software costs. Amounts capitalized to internal use software related to continuing operations for the years ended December 31, 2019 and 2018 were $3,800 and $6,690, respectively. Financial table: uid: 74a3ff891297168a52a0a014b4919f78 table: December 31 Useful life (in years) 2019 2018 Computer equipment and software 3-5 14,689 14,058 Furniture and equipment 5-7 2,766 3,732 Leasehold and building improvements (1) 7,201 7,450 Construction in progress - PPE 949 — Property, plant, and equipment, excluding internal use software 25,605 25,240 Less: Accumulated depreciation and amortization (19,981) (17,884) Property, plant and equipment, excluding internal use software, net 5, ...

### Document 8

- ID: `tatqa_185_1__semantic_noise__7`
- Role: `semantic_distractor`
- Source: `semantic_noise_from_tatqa`
- Title: TAT-QA document 213, question 5

Paragraph evidence: Note 8. Property, Plant and Equipment, net Property, plant and equipment, net as of December 31, 2019 and 2018 consisted of the following: (1) Useful lives for leasehold and building improvements represent the term of the lease or the estimated life of the related improvements, whichever is shorter. Depreciation expense from continuing operations was $12,548 and $12,643 for the years ended December 31, 2019 and 2018, respectively, of which $9,028 and $9,189, respectively, related to internal use software costs. Amounts capitalized to internal use software related to continuing operations for the years ended December 31, 2019 and 2018 were $3,800 and $6,690, respectively. Financial table: uid: 74a3ff891297168a52a0a014b4919f78 table: December 31 Useful life (in years) 2019 2018 Computer equipment and software 3-5 14,689 14,058 Furniture and equipment 5-7 2,766 3,732 Leasehold and building improvements (1) 7,201 7,450 Construction in progress - PPE 949 — Property, plant, and equipment, excluding internal use software 25,605 25,240 Less: Accumulated depreciation and amortization (19,981) (17,884) Property, plant and equipment, excluding internal use software, net 5, ...

**Human judgment:** PASS / FAIL / UNCERTAIN

**Reason:**

---

## Case 40: tatqa / noisy

**Instance ID:** `tatqa_251_1__noisy`

**Question:** What were the net sales in 2019?

**Gold answer:** 5,563.7

**Expected abstention:** False

**Evidence:**

### Document 1

- ID: `tatqa_251_1_gold_0`
- Role: `support`
- Source: `tatqa`
- Title: TAT-QA document 251, question 1

Paragraph evidence: Note 2. Business Acquisitions Acquisition of Microsemi The following unaudited pro-forma consolidated results of operations for the fiscal year ended March 31, 2019 and 2018 assume the closing of the Microsemi acquisition occurred as of April 1, 2017. The pro-forma adjustments are mainly comprised of acquired inventory fair value costs and amortization of purchased intangible assets. The pro-forma results of operations are presented for informational purposes only and are not indicative of the results of operations that would have been achieved if the acquisition had taken place on April 1, 2017 or of results that may occur in the future (in millions except per share data): Financial table: uid: f4f9757a1ce1c82e6d901aca9b1020e3 table: Year Ended March 31, 2019 2018 Net sales $5,563.7 $5,875.0 Net income (loss) $542.0 $(762.3) Basic net income (loss) per common share $2.29 $(3.27) Diluted net income (loss) per common share $2.17 $(3.27)

### Document 2

- ID: `tatqa_251_1__semantic_noise__0`
- Role: `semantic_distractor`
- Source: `semantic_noise_from_tatqa`
- Title: TAT-QA document 7, question 1

Paragraph evidence: Results of Operations Year Ended March 31, 2019 compared to Year Ended March 31, 2018 Net sales for the fiscal year ended March 31, 2019 were $1,791.8 million compared to $1,562.5 million for the fiscal year ended March 31, 2018. Electronic Component sales were $1,290.0 million for the fiscal year ended March 31, 2019 compared to $1,235.2 million during the fiscal year ended March 31, 2018. Fiscal year 2019 Advanced Components group sales include $113.3 million of Ethertronics product as compared to $12.7 million for fiscal year 2018. These increases were partially offset by the loss of Kyocera resale product sales which were $19.0 million for fiscal year 2019 as compared to $296.3 million for fiscal year 2018. Total Interconnect, Sensing and Control Devices product sales were $501.8 million in the fiscal year 2019 as compared to $327.3 million during the fiscal year 2018. This increase is attributable to sales growth in the automotive industry in addition to sales resulting from our S&C acquisition which accounted for $354.7 million for fiscal year 2019 as compared to $193.3 million for fiscal year 2018. Our sales to independent electronic distributors represen ...

### Document 3

- ID: `tatqa_251_1__semantic_noise__1`
- Role: `semantic_distractor`
- Source: `semantic_noise_from_tatqa`
- Title: TAT-QA document 74, question 5

Paragraph evidence: Net sales Net sales of $1.2 billion for fiscal year 2018 increased 58.5% from $757.3 million for fiscal year 2017. Solid Capacitor and Film and Electrolytic sales increased by $196.1 million and $19.7 million, respectively and net sales for MSA, our new reportable segment in fiscal year 2018, was $227.0 million. Prior to the acquisition of TOKIN on April 19, 2017, the Company did not have any MSA sales. The increase in Solid Capacitors net sales was primarily driven by the addition of net sales of $133.8 million resulting from the TOKIN acquisition and an increase in net sales to the legacy products distributor channel of $81.7 million. To a lesser degree, an increase in legacy Ceramic products' net sales of $6.0 million in the EMS channel across all regions and $10.2 million in the OEM channel in the EMEA and APAC regions also contributed to the increase in Solid Capacitors net sales. These increases were partially offset by a $28.0 million decrease in net sales in the OEM channel for legacy Tantalum products across all regions. In addition, Solid Capacitors net sales was favorably impacted by $6.1 million from foreign currency exchange due to the change in the ...

### Document 4

- ID: `tatqa_251_1__semantic_noise__2`
- Role: `semantic_distractor`
- Source: `semantic_noise_from_tatqa`
- Title: TAT-QA document 74, question 4

Paragraph evidence: Net sales Net sales of $1.2 billion for fiscal year 2018 increased 58.5% from $757.3 million for fiscal year 2017. Solid Capacitor and Film and Electrolytic sales increased by $196.1 million and $19.7 million, respectively and net sales for MSA, our new reportable segment in fiscal year 2018, was $227.0 million. Prior to the acquisition of TOKIN on April 19, 2017, the Company did not have any MSA sales. The increase in Solid Capacitors net sales was primarily driven by the addition of net sales of $133.8 million resulting from the TOKIN acquisition and an increase in net sales to the legacy products distributor channel of $81.7 million. To a lesser degree, an increase in legacy Ceramic products' net sales of $6.0 million in the EMS channel across all regions and $10.2 million in the OEM channel in the EMEA and APAC regions also contributed to the increase in Solid Capacitors net sales. These increases were partially offset by a $28.0 million decrease in net sales in the OEM channel for legacy Tantalum products across all regions. In addition, Solid Capacitors net sales was favorably impacted by $6.1 million from foreign currency exchange due to the change in the ...

### Document 5

- ID: `tatqa_251_1__semantic_noise__3`
- Role: `semantic_distractor`
- Source: `semantic_noise_from_tatqa`
- Title: TAT-QA document 67, question 5

Paragraph evidence: In 2019, gross margin decreased by 130 basis points to 38.7% from 40.0% in the full year 2018 mainly due to normal price pressure and increased unsaturation charges, partially offset by improved manufacturing efficiencies, better product mix, and favorable currency effects, net of hedging. Unused capacity charges in 2019 were $65 million, impacting full year gross margin by 70 basis points. In 2018, gross margin improved by 80 basis points to 40.0% from 39.2% in the full year 2017 benefiting from manufacturing efficiencies and better product mix, partially offset by normal price pressure and unfavorable currency effects, net of hedging. In 2018 unused capacity charges were negligible. Financial table: uid: e65078d0c208393b185d7519fe2f78d5 table: Year Ended December 31, Year Ended December 31, Year Ended December 31, Variation Variation 2019 2018 2017 2019 vs 2018 2018 vs 2017 (In millions) (In millions) (In millions) Cost of sales $(5,860) $(5,803) $(5,075) 1.0% (14.3)% Gross profit $3,696 $3,861 $3,272 (4.3)% 18.0% Gross margin (as percentage of net revenues) 38.7% 40.0% 39.2% -130 bps +80 bps

### Document 6

- ID: `tatqa_251_1__semantic_noise__4`
- Role: `semantic_distractor`
- Source: `semantic_noise_from_tatqa`
- Title: TAT-QA document 95, question 2

Paragraph evidence: There was no material bad debt expense in 2019, 2018 and 2017. In 2019, 2018 and 2017, the Company’s largest customer, Apple represented 17.6%, 13.1% and 10.5% of consolidated net revenues, respectively, reported in the ADG, AMS and MDG segments. In 2019, $75 million of trade accounts receivable were sold without recourse (nil in 2018). Financial table: uid: dd59f51fb5ae5c0435b09ab86bb62380 table: December 31, 2019 December 31, 2018 Trade accounts receivable 1,396 1,292 Allowance for doubtful accounts (16) (15) Total 1,380 1,277

### Document 7

- ID: `tatqa_251_1__semantic_noise__5`
- Role: `semantic_distractor`
- Source: `semantic_noise_from_tatqa`
- Title: TAT-QA document 109, question 2

Paragraph evidence: ITEM 7 MANAGEMENT’S DISCUSSION AND ANALYSIS OF FINANCIAL CONDITION AND RESULTS OF OPERATIONS The following discussion of the financial condition and results of operations for the years ended December 31, 2019 and December 31, 2018 should be read in conjunction with the audited consolidated financial statements and the notes to those statements that are included elsewhere in this report on Form 10-K. Results of Operations Comparison of Year Ended December 31, 2019 to Year Ended December 31, 2018 (in 000’s) Net Sales Net sales were $93,662 for the year ended December 31, 2019, a decrease of $9,688 or 9.4% versus prior year. Gross Profit Gross profit as a percentage of net sales decreased to 23.6% during the year ended December 31, 2019 from 25.0% during the same period in 2018. The lower gross profit percentage primarily reflects category sales softness, the unfavorable impact of operating leverage that arises from lower net sales relative to fixed costs, and increased freight costs and depreciation, partially offset by a reduction in variable costs. Selling Expenses Selling expenses decreased by $2,415 or 17.9% to $11,062 during the year ended December 31, 2019 f ...

### Document 8

- ID: `tatqa_251_1__semantic_noise__6`
- Role: `semantic_distractor`
- Source: `semantic_noise_from_tatqa`
- Title: TAT-QA document 103, question 2

Paragraph evidence: Consolidated Net Revenues The key drivers of changes in our consolidated net revenues, operating segment results, consolidated results, and sources of liquidity are presented in the order of significance. The following table summarizes our consolidated net revenues, increase (decrease) in associated deferred net revenues recognized, and in-game net revenues (amounts in millions): (1) In-game net revenues primarily includes the net amount of revenue recognized for downloadable content and microtransactions during the period. Consolidated net revenues The decrease in consolidated net revenues for 2019, as compared to 2018, was primarily driven by a decrease in revenues of $1.1 billion due to: • lower revenues recognized from the Destiny franchise (reflecting our sale of the publishing rights for Destiny to Bungie in December 2018); • lower revenues recognized from Hearthstone; • lower revenues recognized from Call of Duty franchise catalog titles; and • lower revenues recognized from Overwatch. The decrease was partially offset by an increase in revenues of $236 million due to: • revenues from Sekiro: Shadows Die Twice, which was released in March 2019; and • reve ...

### Document 9

- ID: `tatqa_251_1__semantic_noise__7`
- Role: `semantic_distractor`
- Source: `semantic_noise_from_tatqa`
- Title: TAT-QA document 60, question 2

Paragraph evidence: 6 Segment Information continued The Group’s revenue is diversified across its entire end customer base and no single end user accounted for greater than 10 per cent of the Group’s revenue in either 2018 or 2019. In 2019 two distributors accounted for 15 per cent each, and one distributor for 11 per cent of Group billings which were attributable to all segments of the Group (2018: three distributors accounted for 15 per cent, 14 per cent and 12 per cent each). Financial table: uid: 4bac0b8169e05a0e8d1220fab5e165d5 table: Year-ended 31 March 2019 Year-ended 31 March 2018 Restated See note 2 Revenue from external customers by country $M $M UK 83.2 73.5 USA 222.2 199.0 Germany 143.5 128.4 Other countries 261.7 238.1 Total revenue from external customers by country 710.6 639.0

**Human judgment:** PASS / FAIL / UNCERTAIN

**Reason:**

---

## Case 41: tatqa / partial

**Instance ID:** `tatqa_145_3__partial`

**Question:** What was the change in revenue from software maintenance between 2018 and 2019?

**Gold answer:** 432

**Expected abstention:** True

**Retained ratio:** 0.5375347544022243

**Evidence:**

### Document 1

- ID: `tatqa_145_3__partial__tatqa_145_3_gold_0`
- Role: `partial_support`
- Source: `tatqa_partial_v3`
- Title: TAT-QA document 145, question 3 | partial evidence

Paragraph evidence: R. Segment Information VMware operates in one reportable operating segment, thus all required financial segment information is included in the consolidated financial statements. Operating segments are defined as components of an enterprise for which separate financial information is evaluated regularly by the chief operating decision maker in deciding how to allocate resources and assessing performance. VMware’s chief operating decision maker allocates resources and assesses performance based upon discrete financial information at the consolidated level.

### Document 2

- ID: `tatqa_145_3__semantic_noise__0`
- Role: `semantic_distractor`
- Source: `semantic_noise_from_tatqa`
- Title: TAT-QA document 239, question 5

Paragraph evidence: Years Ended December 31, 2019 and 2018: Revenue Services. Services revenue consists primarily of fees for customer support services generated from our partners. We provide these services remotely, generally using personnel who utilize our proprietary technology to deliver the services. Services revenue is also comprised of licensing of our Support.com Cloud applications. Services revenue for the year ended December 31, 2019 decreased by $4.9 million from 2018. The decrease in service revenue was primarily due to the decrease in the billable hours of our major customers. For the year ended December 31, 2019, services revenue generated from our partnerships was $56.6 million compared to $61.0 million for 2018. For the year ended December 31, 2019, direct services revenue was $2.9 million compared to $3.5 million for 2018. As with any market that is undergoing shifts, timing of downward pressures and growth opportunities in our services programs are difficult to predict. We are experiencing downward pressure with some of our services programs as personal computer and certain retail markets are subject to internal re-alignment and other sector specific softness. How ...

### Document 3

- ID: `tatqa_145_3__semantic_noise__1`
- Role: `semantic_distractor`
- Source: `semantic_noise_from_tatqa`
- Title: TAT-QA document 239, question 1

Paragraph evidence: Years Ended December 31, 2019 and 2018: Revenue Services. Services revenue consists primarily of fees for customer support services generated from our partners. We provide these services remotely, generally using personnel who utilize our proprietary technology to deliver the services. Services revenue is also comprised of licensing of our Support.com Cloud applications. Services revenue for the year ended December 31, 2019 decreased by $4.9 million from 2018. The decrease in service revenue was primarily due to the decrease in the billable hours of our major customers. For the year ended December 31, 2019, services revenue generated from our partnerships was $56.6 million compared to $61.0 million for 2018. For the year ended December 31, 2019, direct services revenue was $2.9 million compared to $3.5 million for 2018. As with any market that is undergoing shifts, timing of downward pressures and growth opportunities in our services programs are difficult to predict. We are experiencing downward pressure with some of our services programs as personal computer and certain retail markets are subject to internal re-alignment and other sector specific softness. How ...

**Human judgment:** PASS / FAIL / UNCERTAIN

**Reason:**

---

## Case 42: tatqa / stale

**Instance ID:** `tatqa_48_3__stale`

**Question:** What was the change in the Adjusted operating income (tax effected) between 2018 and 2019?

**Gold answer:** 2.1

**Expected abstention:** True

**Evidence:**

### Document 1

- ID: `tatqa_48_3__stale_doc`
- Role: `stale`
- Source: `synthetic_controlled_stale_v3`
- Title: Archived source snapshot (2018)

Snapshot date: 2018-06-30. Question recorded: What was the change in the Adjusted operating income (tax effected) between 2018 and 2019? Reported answer in this snapshot: 590

### Document 2

- ID: `tatqa_48_3__semantic_noise__0`
- Role: `semantic_distractor`
- Source: `semantic_noise_from_tatqa`
- Title: TAT-QA document 169, question 5

Paragraph evidence: The following table sets forth a summary of our cash flows for the periods indicated (in thousands): Our cash flows from operating activities are significantly influenced by our growth, ability to maintain our contractual billing and collection terms, and our investments in headcount and infrastructure to support anticipated growth. Given the seasonality and continued growth of our business, our cash flows from operations will vary from period to period. Cash provided by operating activities was $115.5 million in 2019, compared to $90.3 million in 2018. The increase in operating cash flow was primarily due to improved profitability, improved collections, and other working capital changes in 2019 when compared to 2018. Financial table: uid: 4b528eb35807a61dcad7b7f9c3b994a2 table: Year Ended December 31, 2019 2018 2017 Net cash provided by operating activities $115,549 $90,253 $67,510 Net cash used in investing activities (97,727) (20,876) (36,666) Net cash provided by (used in) financing activities 14,775 (278,016) 276,852

### Document 3

- ID: `tatqa_48_3__semantic_noise__1`
- Role: `semantic_distractor`
- Source: `semantic_noise_from_tatqa`
- Title: TAT-QA document 26, question 4

Paragraph evidence: Results of Operations The following table sets forth the percentage of revenue for certain items in our statements of operations for the periods indicated: Impact of inflation and product price changes on our revenue and on income was immaterial in 2019, 2018 and 2017. Financial table: uid: 4d41ea7a63b2d9b5cc3cb24ca6c7e9ac table: Fiscal Years 2019 2018 2017 Statements of Operations: Revenue 100% 100% 100% Cost of revenue 43% 50% 55% Gross profit 57% 50% 45% Operating expenses: Research and development 120% 79% 79% Selling, general and administrative 86% 79% 81% Loss from operations (149)% (108)% (115)% Interest expense (3)% (1)% (1)% Interest income and other expense, net 2% 1% —% Loss before income taxes (150)% (108)% (116)% Provision for income taxes 1% 1% 1% Net loss (151)% (109)% (117)%

### Document 4

- ID: `tatqa_48_3__semantic_noise__2`
- Role: `semantic_distractor`
- Source: `semantic_noise_from_tatqa`
- Title: TAT-QA document 46, question 0

Paragraph evidence: Non-GAAP operating income, net income, and diluted earnings per share (“EPS”) exclude the net tax impact of transfer of intangible properties, the net tax impact of the TCJA, and restructuring expenses. Fiscal Year 2019 Compared with Fiscal Year 2018 Revenue increased $15.5 billion or 14%, driven by growth across each of our segments. Key changes in expenses were: • Cost of revenue increased $4.6 billion or 12%, driven by growth in commercial cloud, Surface, and Gaming. • Research and development expenses increased $2.2 billion or 15%, driven by investments in cloud and artificial intelligence (“AI”) engineering, Gaming, LinkedIn, and GitHub. • Sales and marketing expenses increased $744 million or 4%, driven by investments in commercial sales capacity, LinkedIn, and GitHub, offset in part by a decrease in marketing. Sales and marketing expenses included a favorable foreign currency impact of 2%. Current year net income included a $2.6 billion net income tax benefit related to intangible property transfers and a $157 million net charge related to the enactment of the TCJA, which together resulted in an increase to net income and diluted EPS of $2.4 billion and $ ...

### Document 5

- ID: `tatqa_48_3__semantic_noise__3`
- Role: `semantic_distractor`
- Source: `semantic_noise_from_tatqa`
- Title: TAT-QA document 3, question 1

The results of our acquired companies have been included in our consolidated financial statements since their respective dates of acquisition and have contributed to our revenues, income, earnings per share and total assets. (1) Our net income and diluted earnings per share were impacted in fiscal 2019 and 2018 by the effects of the U.S. Tax Cuts and Jobs Act of 2017 (the Tax Act). (2) Working capital and total assets decreased in fiscal 2019 primarily due to $36.1 billion of cash used for repurchases of our common stock during fiscal 2019 and also due to dividend payments, partially offset by the favorable impacts to our net current assets resulting from our fiscal 2019 net income. Working capital and total assets sequentially increased in nearly all of the fiscal 2015 to 2018 periods presented primarily due to the favorable impacts to our net current assets resulting from our net income generated during the periods presented and the issuances of long-term senior notes of $10.0 billion in fiscal 2018, and $14.0 billion in fiscal 2017. These working capital and total assets increases were partially offset by cash used for acquisitions, repurchases of our common stock and dividend p ...

### Document 6

- ID: `tatqa_48_3__semantic_noise__4`
- Role: `semantic_distractor`
- Source: `semantic_noise_from_tatqa`
- Title: TAT-QA document 18, question 5

Paragraph evidence: Note 7—Income Taxes The Company is incorporated in Switzerland but operates in various countries with differing tax laws and rates. Further, a portion of the Company's income (loss) before taxes and the provision for (benefit from) income taxes is generated outside of Switzerland. Income from continuing operations before income taxes for fiscal years 2019 , 2018 and 2017 is summarized as follows (in thousands): Financial table: uid: 354eb1815ff939a06de1e27501c65ece table: Years Ended March 31, 2019 2018 2017 Swiss $212,986 $177,935 $161,544 Non-Swiss 58,147 54,330 53,445 Income before taxes $271,133 $232,265 $214,989

### Document 7

- ID: `tatqa_48_3__semantic_noise__5`
- Role: `semantic_distractor`
- Source: `semantic_noise_from_tatqa`
- Title: TAT-QA document 18, question 0

Paragraph evidence: Note 7—Income Taxes The Company is incorporated in Switzerland but operates in various countries with differing tax laws and rates. Further, a portion of the Company's income (loss) before taxes and the provision for (benefit from) income taxes is generated outside of Switzerland. Income from continuing operations before income taxes for fiscal years 2019 , 2018 and 2017 is summarized as follows (in thousands): Financial table: uid: 354eb1815ff939a06de1e27501c65ece table: Years Ended March 31, 2019 2018 2017 Swiss $212,986 $177,935 $161,544 Non-Swiss 58,147 54,330 53,445 Income before taxes $271,133 $232,265 $214,989

### Document 8

- ID: `tatqa_48_3__semantic_noise__6`
- Role: `semantic_distractor`
- Source: `semantic_noise_from_tatqa`
- Title: TAT-QA document 58, question 2

Paragraph evidence: Results of Continuing Operations The analysis presented below is organized to provide the information we believe will facilitate an understanding of our historical performance and relevant trends going forward, and should be read in conjunction with our Consolidated Financial Statements, including the notes thereto, in Item 8 "Financial Statements and Supplementary Data" of this Annual Report on Form 10 - K. The following table sets forth, for the periods indicated, the percentage of sales represented by certain items reflected in our Consolidated Statements of Operations: Financial table: uid: 525032451ab45a3ba6d2629c06d68d1d table: Year Ended December 31, 2019 2018 Sales 100.0 % 100.0 % Gross profit 40.0 50.9 Operating expenses 33.1 27.0 Operating income from continuing operations 6.9 23.9 Other income (expense), net 1.6 0.1 Income from continuing operations before income taxes 8.5 24.0 Provision for income taxes 1.4 3.5 Income from continuing operations, net of income taxes 7.2 % 20.5 %

### Document 9

- ID: `tatqa_48_3__semantic_noise__7`
- Role: `semantic_distractor`
- Source: `semantic_noise_from_tatqa`
- Title: TAT-QA document 18, question 1

Paragraph evidence: Note 7—Income Taxes The Company is incorporated in Switzerland but operates in various countries with differing tax laws and rates. Further, a portion of the Company's income (loss) before taxes and the provision for (benefit from) income taxes is generated outside of Switzerland. Income from continuing operations before income taxes for fiscal years 2019 , 2018 and 2017 is summarized as follows (in thousands): Financial table: uid: 354eb1815ff939a06de1e27501c65ece table: Years Ended March 31, 2019 2018 2017 Swiss $212,986 $177,935 $161,544 Non-Swiss 58,147 54,330 53,445 Income before taxes $271,133 $232,265 $214,989

**Human judgment:** PASS / FAIL / UNCERTAIN

**Reason:**

---

