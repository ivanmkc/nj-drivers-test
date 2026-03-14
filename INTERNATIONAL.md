# International Driver Manual Index

Worldwide index of official driver manuals/handbooks available in English from government transport authorities. PDF URLs listed here were found via search but **have not been verified as downloadable** — most government sites block automated downloads and require a browser.

To add a jurisdiction: download the PDF manually in a browser, place it at `/tmp/<code>_manual.pdf`, then run:
```bash
python3 tools/setup_state.py <code> "<name>" "<agency>" <pass_pct> <test_count> "<manual_url>" "<source_desc>"
```

## Canada

| Code | Province | Agency | Manual URL | Status |
|------|----------|--------|------------|--------|
| ca-bc | British Columbia | ICBC | https://www.icbc.com/driver-licensing/Documents/drivers-handbook.pdf | Not sourced |
| ca-ab | Alberta | Transportation | https://open.alberta.ca/publications/drivers-guide-cars-light-trucks | Not sourced |
| ca-on | Ontario | MTO | Online only (ontario.ca/drivers-handbook) | Not sourced |
| ca-qc | Quebec | SAAQ | https://saaq.gouv.qc.ca (French primary, English available) | Not sourced |
| ca-mb | Manitoba | MPI | https://www.mpi.mb.ca/driver-handbook | Not sourced |
| ca-sk | Saskatchewan | SGI | https://www.sgi.sk.ca/handbook | Not sourced |
| ca-ns | Nova Scotia | Access NS | https://novascotia.ca/sns/rmv/handbook | Not sourced |
| ca-nb | New Brunswick | SNB | https://www2.gnb.ca/content/gnb/en/departments/public-safety/drivers-handbook.html | Not sourced |

## Australia

| Code | State | Agency | Manual URL | Status |
|------|-------|--------|------------|--------|
| au-nsw | New South Wales | Transport for NSW | https://www.nsw.gov.au/driving-boating-and-transport/roads-safety-and-rules/road-users-handbook | Not sourced |
| au-vic | Victoria | VicRoads | https://www.vicroads.vic.gov.au/licences/road-to-solo-driving | Not sourced |
| au-qld | Queensland | TMR | https://www.publications.qld.gov.au (Your Keys to Driving in Queensland) | Not sourced |
| au-wa | Western Australia | DoT | https://www.transport.wa.gov.au/licensing/drive-safe-handbook.asp | Not sourced |
| au-sa | South Australia | DIT | https://www.sa.gov.au/topics/driving-and-transport/licences/car-and-motorcycle/getting-your-licence | Not sourced |

## United Kingdom & Ireland

| Code | Region | Agency | Manual URL | Status |
|------|--------|--------|------------|--------|
| uk | United Kingdom | DVSA | Highway Code (gov.uk/highway-code) — not free PDF | Not sourced |
| ie | Ireland | RSA | https://www.rsa.ie/road-safety/rules-of-the-road | Not sourced |

## New Zealand

| Code | Region | Agency | Manual URL | Status |
|------|--------|--------|------------|--------|
| nz | New Zealand | NZTA | https://www.nzta.govt.nz/resources/driving-in-nz | Not sourced |

## Asia

| Code | Country/Region | Agency | Manual URL | Status |
|------|----------------|--------|------------|--------|
| sg | Singapore | Traffic Police | https://www.police.gov.sg (Basic Theory of Driving) | Not sourced |
| hk | Hong Kong | Transport Dept | https://www.td.gov.hk (Road Users' Code) | Not sourced |
| ph | Philippines | LTO | https://lto.gov.ph (Filipino Driver's Manual) | Not sourced |
| jp | Japan | JAF/NPA | "Rules of the Road" (English, limited availability) | Not sourced |
| kr | South Korea | KoROAD | Driving guide for foreigners (Korean primary) | Not sourced |
| in | India | MoRTH | No centralized English PDF found | Not sourced |

## Middle East

| Code | Country/Region | Agency | Manual URL | Status |
|------|----------------|--------|------------|--------|
| ae | UAE / Dubai | RTA | Light Motor Vehicle Handbook (not free PDF) | Not sourced |

## Africa

| Code | Country | Agency | Manual URL | Status |
|------|---------|--------|------------|--------|
| za | South Africa | DoT | K53 Manual (not free PDF) | Not sourced |
| ng | Nigeria | FRSC | Nigeria Highway Code (not free PDF found) | Not sourced |

## Europe

| Code | Country | Agency | Manual URL | Status |
|------|---------|--------|------------|--------|
| de | Germany | BMDV | No free English PDF (driving schools provide materials) | Not sourced |
| nl | Netherlands | CBR | No free English PDF found | Not sourced |
| se | Sweden | Transportstyrelsen | No free English PDF found | Not sourced |
| no | Norway | Statens vegvesen | No free English PDF found | Not sourced |

## Latin America

| Code | Country | Agency | Manual URL | Status |
|------|---------|--------|------------|--------|
| mx | Mexico | SCT | No English PDF found | Not sourced |
| br | Brazil | DETRAN | No English PDF found | Not sourced |

---

**Most promising targets** (official English PDFs likely exist behind JS-rendered pages):
1. Canada: BC, Alberta, Ontario
2. Australia: NSW, Victoria, Queensland
3. New Zealand
4. Ireland
5. Singapore
6. Hong Kong
7. Philippines
