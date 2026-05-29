/**
 * KOTIBHASKAR INDUSTRIES — COMPLETE WEBSITE PATCH
 * File: kotibhaskar-patch.js
 * 
 * HOW TO DEPLOY:
 * Add this line just before </body> in your index.html:
 *   <script src="kotibhaskar-patch.js"></script>
 * 
 * This patch:
 *  1. Fixes Material Handling Trolleys tab (was dead)
 *  2. Fixes Wheels & Castors tab (was dead)
 *  3. Adds full product data for all 3 categories
 *  4. Fixes product modal — opens with real specs
 *  5. Fixes Print as PDF — clean datasheet layout
 *  6. Fixes Send Enquiry — pre-fills product name
 *  7. Fixes enquiry form submission via EmailJS
 *  8. Fixes Our Story contrast
 *  9. Removes Manufacturing Facility section
 * 10. Fixes smart product finder
 * 11. Fully responsive (desktop / tablet / mobile)
 * 
 * EMAIL SETUP (required for real sending):
 *  - Go to https://emailjs.com → Create free account
 *  - Add Email Service (Gmail) → copy SERVICE_ID
 *  - Create Email Template → copy TEMPLATE_ID
 *  - Copy your PUBLIC_KEY from Account > API Keys
 *  - Replace the 3 placeholders below:
 */

const EMAILJS_SERVICE_ID  = 'YOUR_SERVICE_ID';   // ← replace
const EMAILJS_TEMPLATE_ID = 'YOUR_TEMPLATE_ID';  // ← replace
const EMAILJS_PUBLIC_KEY  = 'YOUR_PUBLIC_KEY';   // ← replace

/* ============================================================
   PRODUCT DATABASE — sourced from kotibhaskar.in
   ============================================================ */

const PRODUCTS = {

  /* ---- CATEGORY 1: Material Handling Equipment ---- */
  mhe: [
    {
      id: 'hydraulic-pallet-truck',
      name: 'Hydraulic Pallet Truck',
      img: 'https://kotibhaskar.in/images/slideshow/02.png',
      desc: 'Heavy-duty hydraulic pallet truck for moving loaded pallets across flat surfaces. Operated manually with a pump handle. Ideal for warehouses, loading docks, and factories.',
      features: [
        'Manual pump operation — no electricity required',
        'Sturdy steel fork frame with reinforced welds',
        'Precision hydraulic cylinder for smooth lifting',
        'Low-profile entry forks for euro & standard pallets',
        'Steer axle with polyurethane drive wheel',
        'Safety overload valve prevents overloading',
        'Powder-coated finish for corrosion resistance'
      ],
      specs: [
        ['Capacity', '2500 kg / 3000 kg'],
        ['Fork Length', '1150 mm'],
        ['Fork Width (OA)', '520 mm / 685 mm'],
        ['Fork Width (IC)', '380 mm / 540 mm'],
        ['Lowered Height', '85 mm'],
        ['Raised Height', '200 mm'],
        ['Drive Wheel', 'Ø200 × 50 PU'],
        ['Load Wheels', 'Ø80 × 70 PU']
      ],
      applications: 'Warehouses, loading bays, factories, cold storage, FMCG distribution, manufacturing shopfloors'
    },
    {
      id: 'electric-pallet-truck',
      name: 'Electric Pallet Truck',
      img: 'https://kotibhaskar.in/images/slideshow/01.png',
      desc: 'Battery-powered electric pallet truck for effortless movement of heavy loads over long distances. Reduces operator fatigue and increases throughput significantly.',
      features: [
        'AC/DC electric drive motor',
        'Maintenance-free gel/lead-acid battery',
        'Electronic speed control with creep speed',
        'Ergonomic tiller arm with thumb-operated controls',
        'Automatic regenerative braking',
        'Hour meter and battery discharge indicator',
        'Safety electromagnetic brake'
      ],
      specs: [
        ['Capacity', '2000 kg'],
        ['Battery', '24V / 150Ah'],
        ['Travel Speed (laden)', '5 km/h'],
        ['Lifting Height', '200 mm'],
        ['Fork Length', '1150 mm'],
        ['Drive Wheel', 'Ø230 × 75 PU'],
        ['Charger', 'On-board 24V/25A']
      ],
      applications: 'Large warehouses, supermarkets, airports, distribution centres, cold chain logistics'
    },
    {
      id: 'manual-stacker',
      name: 'Manual Stacker (Hydraulic)',
      img: 'https://kotibhaskar.in/images/slideshow/04.png',
      desc: 'Manual hydraulic stacker for lifting and stacking loads at height. Pump handle operated, no power required. Cost-effective solution for light-to-medium stacking operations.',
      features: [
        'Manual pump with foot-operated lowering valve',
        'Mast: single or double-stage options',
        'Load-backrest for stability during lift',
        'Straddle legs with adjustable width',
        'Polyurethane load and steer wheels',
        'Safety lowering speed valve',
        'Compact footprint — suits narrow aisles'
      ],
      specs: [
        ['Capacity', '500 – 1000 kg'],
        ['Lift Height', '1600 – 3000 mm'],
        ['Fork Length', '1150 mm'],
        ['Overall Width', '760 – 1210 mm'],
        ['Lowered Fork Height', '85 mm'],
        ['Mast Type', 'Single / Double stage']
      ],
      applications: 'Small warehouses, workshops, mezzanine loading, retail storage, printing & packaging'
    },
    {
      id: 'electric-stacker',
      name: 'Electric Stacker',
      img: 'https://kotibhaskar.in/images/slideshow/03.png',
      desc: 'Full-powered electric stacker with motorised lift and drive. Designed for intensive stacking operations requiring high throughput and operator comfort.',
      features: [
        'Electric lift and drive — full power operation',
        'Full free-lift mast option available',
        'Side-shift attachment option',
        'Auto-height positioning programmable',
        'Regenerative lowering recovers energy',
        'LCD display: battery level, hours, error codes',
        'Cabin or walkie configurations available'
      ],
      specs: [
        ['Capacity', '1000 – 1500 kg'],
        ['Battery', '24V / 210Ah'],
        ['Lift Height', 'Up to 4500 mm'],
        ['Travel Speed', '6 km/h'],
        ['Lift Speed', '0.12 m/s'],
        ['Gradeability', '5%'],
        ['Turning Radius', '1400 mm']
      ],
      applications: 'Warehouses, manufacturing, racking operations, pharmaceutical storage, engineering stores'
    },
    {
      id: 'hydraulic-floor-crane',
      name: 'Hydraulic Floor Crane',
      img: 'https://kotibhaskar.in/images/slideshow/06.png',
      desc: 'Mobile hydraulic floor crane for lifting heavy machinery, engines, and equipment within the shopfloor. Folds compactly for easy storage.',
      features: [
        'Single-piece welded steel boom',
        'Telescopic boom extends reach',
        'Foot-pump hydraulic cylinder',
        'Swivel hook with safety latch',
        '360° manoeuvrable on 4 castors',
        'Adjustable boom angle',
        'Fold-down legs for compact storage'
      ],
      specs: [
        ['Capacity', '500 – 2000 kg (varies with reach)'],
        ['Max. Reach', '1200 – 2200 mm'],
        ['Max. Lift Height', '2200 mm'],
        ['Min. Boom Height', '1060 mm'],
        ['Wheel Type', '150 mm swivel castors'],
        ['Finish', 'Yellow powder coat']
      ],
      applications: 'Machine shops, automotive garages, maintenance workshops, foundries, pump & motor handling'
    },
    {
      id: 'electric-floor-crane',
      name: 'Electric Floor Crane',
      img: 'https://kotibhaskar.in/images/slideshow/05.png',
      desc: 'Battery-powered electric floor crane for precision lifting without manual effort. Ideal for heavy lifts in confined spaces.',
      features: [
        'Electric pump — effortless heavy lifting',
        '24V sealed battery — no emissions indoors',
        'Wireless remote or pendant control',
        'Safety load limiter',
        'Swivel hook with safety latch',
        'Overload protection valve'
      ],
      specs: [
        ['Capacity', '1000 – 2000 kg'],
        ['Battery', '24V / 45Ah'],
        ['Lift Speed', '50 mm/s'],
        ['Max. Reach', '1800 mm'],
        ['Max. Lift Height', '2400 mm']
      ],
      applications: 'Automotive assembly, turbine maintenance, heavy engineering, aircraft MRO, press shops'
    },
    {
      id: 'hydraulic-drum-tilter',
      name: 'Hydraulic Drum Tilter',
      img: 'https://kotibhaskar.in/images/slideshow/08.png',
      desc: 'Hydraulic drum tilter for safe tilting and emptying of 200-litre drums. Eliminates manual tilting — improves safety and reduces spillage.',
      features: [
        'Foot-pump hydraulic tilt mechanism',
        'Drum clamp fits standard 200L steel/plastic drums',
        'Tilt angle: 0–135° adjustable',
        'Anti-slip drum saddle',
        'Wheeled frame for portability',
        'Safety pin prevents accidental lowering'
      ],
      specs: [
        ['Capacity', '300 kg (1 drum)'],
        ['Drum Size', '200L standard drum'],
        ['Tilt Angle', '0 – 135°'],
        ['Frame Material', 'MS fabricated, powder coated'],
        ['Wheels', '4 × Ø150 castors']
      ],
      applications: 'Chemical plants, paint factories, food processing, pharmaceuticals, lubricant depots'
    },
    {
      id: 'electric-drum-tilter',
      name: 'Electric Drum Tilter',
      img: 'https://kotibhaskar.in/images/slideshow/07.png',
      desc: 'Electrically operated drum tilter with push-button control for effortless drum positioning and emptying.',
      features: [
        'Electric motor-driven tilt — zero manual effort',
        'Push-button pendant control',
        'Smooth controlled tilt speed',
        'Emergency stop function',
        'Drum clamp with safety lock',
        'Battery or mains powered options'
      ],
      specs: [
        ['Capacity', '300 kg'],
        ['Tilt Angle', '0 – 135°'],
        ['Power', '0.75 kW / 240V or 24V battery'],
        ['Drum Type', '200L steel / plastic'],
        ['Control', 'Pendant push-button']
      ],
      applications: 'Chemical processing, paint mixing, food & beverage, pharmaceutical batch operations'
    },
    {
      id: 'manual-drum-gripper',
      name: 'Manual Drum Gripper',
      img: 'https://kotibhaskar.in/images/slideshow/10.png',
      desc: 'Attachment for forklifts or stackers to grip and lift steel or plastic drums vertically without damage.',
      features: [
        'Self-locking jaw mechanism — no power needed',
        'Fits standard 200L drums (steel & plastic)',
        'Forklift-mounted via standard carriage',
        'Adjustable jaw spread',
        'Heavy-duty steel construction'
      ],
      specs: [
        ['Capacity', '400 kg (2 drums)'],
        ['Drum Size', '200L standard'],
        ['Jaw Type', 'Self-locking mechanical'],
        ['Mounting', 'ISO Class II fork carriage'],
        ['Finish', 'Yellow powder coat']
      ],
      applications: 'Drum storage yards, chemical warehouses, oil & lubricant depots, solvent factories'
    },
    {
      id: 'electric-drum-gripper',
      name: 'Electric Drum Gripper',
      img: 'https://kotibhaskar.in/images/slideshow/09.png',
      desc: 'Powered drum gripper for safe lifting of drums with electric clamp activation. Reduces operator strain during intensive drum-handling operations.',
      features: [
        'Electric clamp activation via push-button',
        'Motorised jaw opens and closes on command',
        'Safety sensor prevents clamp release when loaded',
        'Fits 200L steel and plastic drums',
        'Forklift or stacker mounting'
      ],
      specs: [
        ['Capacity', '400 kg'],
        ['Power', '24V battery'],
        ['Control', 'Push-button pendant'],
        ['Mounting', 'ISO fork carriage']
      ],
      applications: 'Hazardous chemical handling, paint stores, oil depots, pharmaceutical raw material stores'
    },
    {
      id: 'jib-crane',
      name: 'Jib Crane',
      img: 'https://kotibhaskar.in/images/slideshow/11.png',
      desc: 'Wall-mounted or pillar-mounted jib crane for localised lifting within a defined radius. Space-saving alternative to overhead cranes for workstations.',
      features: [
        'Wall-mounted or free-standing pillar type',
        'Manual or electric chain hoist option',
        'Rotation: 180° (wall) or 270° (pillar)',
        'I-beam boom for rigid load carrying',
        'Adjustable height with stopper',
        'Hot-dip galvanised or powder-coated finish'
      ],
      specs: [
        ['Capacity', '250 – 2000 kg'],
        ['Boom Length', '2000 – 6000 mm'],
        ['Rotation', '180° / 270°'],
        ['Height Under Hook', '3000 – 6000 mm'],
        ['Mounting', 'Wall anchor bolts / Pillar base plate']
      ],
      applications: 'Machine loading/unloading, welding stations, assembly lines, maintenance bays, press shops'
    },
    {
      id: 'gantry',
      name: 'Gantry Crane',
      img: 'https://kotibhaskar.in/images/slideshow/12.png',
      desc: 'Mobile A-frame gantry crane for lifting heavy loads where fixed overhead lifting is unavailable. Adjustable height model available.',
      features: [
        'Welded A-frame structure — high rigidity',
        'Adjustable height cross beam',
        'Rolling castors — fully mobile',
        'Chain hoist or electric hoist mounting point',
        'Knock-down design for easy assembly/disassembly',
        'Powder-coated finish'
      ],
      specs: [
        ['Capacity', '1000 – 5000 kg'],
        ['Span', '2000 – 4000 mm'],
        ['Height (adjustable)', '2500 – 4000 mm'],
        ['Caster Size', 'Ø200 swivel with lock'],
        ['Material', 'Structural MS steel']
      ],
      applications: 'Maintenance workshops, die shops, engineering yards, outdoor erection sites, shipyards'
    },
    {
      id: 'scissor-lift',
      name: 'Scissor Lift',
      img: 'https://kotibhaskar.in/images/slideshow/13.png',
      desc: 'Hydraulic scissor lift table for ergonomic material positioning at any height. Stationary or mobile configurations available.',
      features: [
        'Robust X-frame scissor mechanism',
        'Foot-pump or electric hydraulic operation',
        'Anti-skid chequer plate platform',
        'Safety mechanical lock at working height',
        'Overload protection valve',
        'Optional: turntable, tilt, guard rails'
      ],
      specs: [
        ['Capacity', '500 – 3000 kg'],
        ['Platform Size', 'Custom / standard 1000×800 to 2000×1500'],
        ['Lowered Height', '300 – 500 mm'],
        ['Max Lift Height', '800 – 1500 mm'],
        ['Power', 'Manual / 1-phase / 3-phase electric']
      ],
      applications: 'Assembly lines, loading docks, ergonomic workstations, warehouse picking, vehicle maintenance'
    },
    {
      id: 'dock-leveller',
      name: 'Dock Leveller',
      img: 'https://kotibhaskar.in/images/slideshow/14.png',
      desc: 'Hydraulic dock leveller that bridges the height difference between loading dock and truck floor for smooth forklift/trolley access.',
      features: [
        'Full hydraulic operation — push-button control',
        'Lip extends automatically to truck bed',
        'Safety maintenance strut for inspection',
        'Non-slip chequer plate surface',
        'Bumper rubber absorbs truck impact',
        'Steel pit frame with anchor bolts'
      ],
      specs: [
        ['Capacity', '6000 – 10000 kg'],
        ['Platform Size', '1800×2000 mm / 2000×2000 mm'],
        ['Adjustable Range', '+300 / –250 mm from dock level'],
        ['Lip Length', '400 mm'],
        ['Operation', 'Hydraulic push-button']
      ],
      applications: 'Distribution centres, cold stores, pharmaceutical warehouses, FMCG logistics hubs, ports'
    },
    {
      id: 'goods-lift',
      name: 'Goods Lift',
      img: 'https://kotibhaskar.in/images/slideshow/15.png',
      desc: 'Industrial goods lift (mezzanine lift) for moving materials between floor levels without stairs. Chain-driven or hydraulic mechanism.',
      features: [
        '4-channel or 2-channel mast configurations',
        'Safety gate on each level',
        'Overload protection',
        'Limit switches at top and bottom',
        'Manual push or motorised drive',
        'Platform with anti-slip surface'
      ],
      specs: [
        ['Capacity', '500 – 2000 kg'],
        ['Platform Size', '1200×1200 to 2000×2000 mm'],
        ['Lift Height', '3000 – 6000 mm'],
        ['Mast Type', '2-channel / 4-channel'],
        ['Drive', 'Electric chain hoist or hydraulic']
      ],
      applications: 'Mezzanine floors, multi-level factories, pharma stores, printing houses, engineering facilities'
    },
    {
      id: 'gravity-roller-conveyor',
      name: 'Gravity Roller Conveyor',
      img: 'https://kotibhaskar.in/images/slideshow/19.png',
      desc: 'Non-powered roller conveyor for smooth gravity-assisted movement of boxes, crates, and pallets along assembly or packing lines.',
      features: [
        'Steel rollers on MS frame — no power needed',
        'Adjustable legs for incline setting',
        'Roller pitch customisable',
        'Galvanised or painted roller options',
        'Inline with powered conveyors',
        'Modular sections for easy extension'
      ],
      specs: [
        ['Width', '300 – 800 mm'],
        ['Roller Diameter', '50 mm / 63 mm'],
        ['Roller Pitch', '75 – 150 mm'],
        ['Section Length', '1500 / 3000 mm'],
        ['Capacity/roller', '50 – 100 kg']
      ],
      applications: 'Packing lines, dispatch areas, assembly lines, warehouses, postal sortation'
    },
    {
      id: 'belt-conveyor',
      name: 'Belt Conveyor',
      img: 'https://kotibhaskar.in/images/slideshow/20.png',
      desc: 'Motorised belt conveyor for continuous horizontal or inclined movement of goods. Available in flat and inclined configurations.',
      features: [
        'PVC or rubber belt options',
        'Variable speed with VFD drive',
        'Adjustable height and incline',
        'Belt tensioner for slip-free operation',
        'Side guards prevent goods from falling',
        'Easy belt replacement design'
      ],
      specs: [
        ['Width', '300 – 1000 mm'],
        ['Length', '1500 – 10000 mm'],
        ['Belt Speed', '5 – 30 m/min (adjustable)'],
        ['Motor', '0.37 – 2.2 kW / 3-phase'],
        ['Incline', 'Horizontal to 30°']
      ],
      applications: 'Food processing, packaging, e-commerce fulfilment, manufacturing assembly, parcel sorting'
    },
    {
      id: 'industrial-shelving',
      name: 'Industrial Shelving',
      img: 'https://kotibhaskar.in/images/slideshow/22.png',
      desc: 'Heavy-duty industrial slotted angle or boltless shelving for organised storage of parts, boxes, and materials.',
      features: [
        'Powder-coated steel sections',
        'Boltless or bolted assembly',
        'Adjustable shelf heights',
        'Anti-collapse brace on rear',
        'Starter and add-on bay system',
        'Suitable for manual and pallet storage'
      ],
      specs: [
        ['Load/shelf', '200 – 500 kg'],
        ['Bay Width', '900 – 1800 mm'],
        ['Bay Depth', '400 – 600 mm'],
        ['Height', '1800 – 3000 mm'],
        ['Shelf Material', '1.2 – 2.0 mm CRCA steel']
      ],
      applications: 'Stores, workshops, warehouses, retail back-rooms, spare parts rooms, libraries'
    }
  ],

  /* ---- CATEGORY 2: Material Handling Trolleys ---- */
  trolleys: [
    {
      id: 'platform-trolley',
      name: 'Platform Trolley',
      img: 'https://kotibhaskar.in/images/slideshow/25.png',
      desc: 'Heavy-duty flat platform trolley for transporting boxes, bags, crates, and materials within factories, warehouses, and stores. Available in MS, SS, and PP top variants.',
      features: [
        'Single-piece MS sheet platform, ribbed for strength',
        'Bent C-channel edges for aesthetic finish',
        'Fitted with 2 fixed + 2 swivel castors',
        'Available: plain MS, chequer plate, PP sheet, rubber, plywood tops',
        'Stainless steel variant available',
        'Custom built to customer dimensions',
        'Powder-coated finish'
      ],
      specs: [
        ['Model P-600', '300 kg — 600×450 mm platform'],
        ['Model P-900', '500 kg — 900×600 mm platform'],
        ['Model P-1250', '700 kg — 1250×750 mm platform'],
        ['Model P-1500', '1000 kg — 1500×900 mm platform'],
        ['Platform Height', '170 – 275 mm'],
        ['Handle Height', '950 mm'],
        ['Castor Size', '100×32 to 200×50 mm']
      ],
      applications: 'Factories, godowns, stores, warehouses — moving corrugated boxes, gunny bags, heavy materials, crates'
    },
    {
      id: 'workshop-trolley',
      name: 'Workshop Trolley',
      img: 'https://kotibhaskar.in/images/slideshow/26.png',
      desc: 'Multi-shelf workshop trolley for organising tools, components, and consumables at workstations. Used in CNC shops, maintenance bays, and assembly lines.',
      features: [
        '3–5 tier shelf configuration',
        'MS steel fabricated, powder-coated',
        'Anti-slip ribbed shelf surface',
        '4 swivel castors — 2 with brake',
        'Push handle for easy manoeuvring',
        'Customisable shelf pitch'
      ],
      specs: [
        ['Capacity', '200 – 400 kg'],
        ['Platform Size', '900×500 / 1200×600 mm'],
        ['No. of Shelves', '3 / 4 / 5'],
        ['Shelf Height', '850 – 1000 mm (top shelf)'],
        ['Castor Size', '100×32 mm with brake']
      ],
      applications: 'CNC machine shops, maintenance departments, assembly lines, tool stores, quality labs'
    },
    {
      id: 'shelf-trolley',
      name: 'Shelf Trolley',
      img: 'https://kotibhaskar.in/images/slideshow/27.png',
      desc: 'Two or three-level shelf trolley for carrying components, small boxes, and materials between workstations or departments.',
      features: [
        '2 or 3-tier shelving',
        'MS pipe frame, powder-coated',
        'Side guard rails prevent goods from falling',
        'Push handle on one or both ends',
        '4 swivel castors — 2 with brake',
        'Custom shelf sizes available'
      ],
      specs: [
        ['Capacity', '200 – 300 kg'],
        ['Shelf Size', '750×450 / 900×600 mm'],
        ['No. of Levels', '2 / 3'],
        ['Height', '900 mm'],
        ['Castor', '100×32 mm PU']
      ],
      applications: 'Hospitals, assembly lines, dispatch areas, supermarkets, clean-rooms, pharmaceutical stores'
    },
    {
      id: 'sack-trolley',
      name: 'Sack Trolley',
      img: 'https://kotibhaskar.in/images/slideshow/28.png',
      desc: 'L-shaped sack/hand trolley for tilting and moving single or multiple sacks, boxes, and cylinders. The most versatile hand-operated trolley.',
      features: [
        'L-shaped MS tube frame — high rigidity',
        'Toe plate: MS or galvanised',
        'Rubber-tyred or PU wheels',
        'Rubber foot on handle to protect floors',
        'Optional: stair-climbing wheel set',
        'Optional: strap/bungee cord hook'
      ],
      specs: [
        ['Capacity', '200 – 300 kg'],
        ['Toe Plate Size', '350×250 mm'],
        ['Frame Height', '1100 – 1200 mm'],
        ['Wheel Size', 'Ø200 / Ø250 rubber or PU'],
        ['Weight', '8 – 12 kg']
      ],
      applications: 'Godowns, cold stores, retail, delivery, gas cylinder handling, laundry, FMCG distribution'
    },
    {
      id: 'drum-trolley',
      name: 'Drum Trolley',
      img: 'https://kotibhaskar.in/images/slideshow/30.png',
      desc: 'Specialised trolley for safe and easy handling of 200-litre drums. Prevents drum rolling, tipping, and floor damage.',
      features: [
        'Saddle frame cradles 200L drum securely',
        'Ratchet strap or chain securing option',
        '4 swivel heavy-duty castors',
        'Low loading height for easy drum placement',
        'Push handle at ergonomic height',
        'MS fabricated, powder-coated'
      ],
      specs: [
        ['Capacity', '300 – 400 kg (single drum)'],
        ['Drum Size', '200L standard steel/plastic drum'],
        ['Castor Size', 'Ø150 swivel with brake'],
        ['Platform Height', '200 mm (approx.)'],
        ['Material', 'MS fabricated']
      ],
      applications: 'Chemical plants, oil depots, paint stores, food processing, pharmaceutical raw material handling'
    },
    {
      id: 'multi-utility-trolley',
      name: 'Multi Utility Trolley',
      img: 'https://kotibhaskar.in/images/slideshow/29.png',
      desc: 'Versatile trolley with multiple shelf configurations for general-purpose use in factories, hospitals, and commercial spaces.',
      features: [
        'Multiple shelf configuration options',
        'Removable/adjustable shelves',
        'Side panel options available',
        'Ergonomic push handle',
        'Braking castors for stability',
        'Custom dimensions on request'
      ],
      specs: [
        ['Capacity', '200 – 350 kg'],
        ['Configuration', 'Flat / shelved / slatted'],
        ['Standard Sizes', '900×600 / 1200×600 mm'],
        ['Height', '900 – 1000 mm'],
        ['Castors', '4 × swivel, 2 with brake']
      ],
      applications: 'Hospitals, factories, hotels, commercial kitchens, retail, clean-rooms'
    },
    {
      id: 'gas-cylinder-trolley',
      name: 'Gas Cylinder Trolley',
      img: 'https://kotibhaskar.in/images/slideshow/31.png',
      desc: 'Purpose-built trolley for safe handling of gas cylinders. Prevents cylinder falling, rolling, and valve damage.',
      features: [
        'Cylinder cradle with safety chain',
        'Handles single or twin cylinder',
        'Tilting handle for easy tip-and-move',
        'Non-spark rubber wheels',
        'MS tube frame, powder-coated',
        'Optional: cylinder cap holder'
      ],
      specs: [
        ['Capacity', '1 or 2 cylinders (standard D/E size)'],
        ['Wheel Type', 'Ø200 rubber — anti-spark'],
        ['Frame Height', '1150 mm'],
        ['Chain', 'Safety lock chain included']
      ],
      applications: 'Welding shops, hospitals, laboratories, industrial gas depots, construction sites'
    },
    {
      id: 'chip-trolley',
      name: 'Chip Trolley',
      img: 'https://kotibhaskar.in/images/slideshow/33.png',
      desc: 'Open-top tub trolley for collection and disposal of metal chips, swarf, and scrap generated by CNC and machining operations.',
      features: [
        'Deep tub body — large volume capacity',
        'Perforated base drains coolant',
        'Forklift pockets for easy emptying',
        '4 heavy-duty swivel castors',
        'MS or stainless steel options',
        'Dump-by-forklift or tip-by-trolley design'
      ],
      specs: [
        ['Capacity (volume)', '200 – 600 litres'],
        ['Load Capacity', '300 – 800 kg'],
        ['Tub Size', 'Custom per machine output'],
        ['Drain Holes', 'Perforated base — Ø8 mm'],
        ['Fork Pockets', '150×50 mm standard']
      ],
      applications: 'CNC machining centres, lathes, milling, grinding operations, scrap metal collection'
    },
    {
      id: 'cnc-tool-trolley',
      name: 'CNC Tool Trolley',
      img: 'https://kotibhaskar.in/images/slideshow/34.png',
      desc: 'Organised tool storage trolley for CNC machine tools, inserts, gauges, and accessories. Keeps tools close to the machine and reduces search time.',
      features: [
        '5–7 drawer configuration with lock',
        'Foam-lined drawers for tool protection',
        'Tool holder pegs on panel/doors',
        'Heavy-duty ball-bearing drawer slides',
        'Central lock for security',
        '4 swivel castors — 2 with lock',
        'Steel top work surface'
      ],
      specs: [
        ['Drawers', '5 / 7 drawers'],
        ['Trolley Size', '700×450×900 mm (approx.)'],
        ['Drawer Load', '30 kg each'],
        ['Top Surface', '10 mm MS plate'],
        ['Material', 'CRCA steel, powder-coated'],
        ['Lock', 'Central key lock']
      ],
      applications: 'CNC machining centres, tool rooms, precision engineering shops, die & mould shops'
    },
    {
      id: 'steel-pallet',
      name: 'Steel Pallet',
      img: 'https://kotibhaskar.in/images/slideshow/35.png',
      desc: 'Heavy-duty MS steel pallet for long-term material storage and movement. Replaces wooden pallets in harsh industrial environments.',
      features: [
        'MS sheet deck with reinforcing ribs',
        'Fork pockets on 2 or 4 sides',
        '4-way pallet truck/forklift entry',
        'Anti-rust primer + powder-coat finish',
        'Stackable design',
        'Custom sizes and capacities available'
      ],
      specs: [
        ['Standard Size', '1200×1000 mm / 1200×800 mm'],
        ['Capacity (static)', '2000 – 5000 kg'],
        ['Capacity (dynamic)', '1000 – 2500 kg'],
        ['Deck Material', '3–5 mm MS plate'],
        ['Finish', 'Primer + powder-coat / galvanised']
      ],
      applications: 'Foundries, heavy engineering, outdoor storage, press shops, chemical drums storage'
    },
    {
      id: 'bin-trolley',
      name: 'Bin Trolley',
      img: 'https://kotibhaskar.in/images/slideshow/40.png',
      desc: 'Wheeled bin trolley for waste collection, recyclables, and scrap movement across the factory floor.',
      features: [
        'Deep bin body — large capacity',
        'Hinged lid option available',
        '4 heavy-duty swivel castors',
        'MS or HDPE bin body options',
        'Handle for easy pushing',
        'Colour-coded lids for segregation'
      ],
      specs: [
        ['Volume', '120 – 660 litres'],
        ['Load Capacity', '100 – 300 kg'],
        ['Bin Material', 'MS / HDPE'],
        ['Castor Size', 'Ø125 – Ø200 mm']
      ],
      applications: 'Waste segregation, recycling stations, food factories, hospitals, municipal services'
    },
    {
      id: 'coolant-trolley',
      name: 'Coolant Trolley',
      img: 'https://kotibhaskar.in/images/slideshow/41.png',
      desc: 'Specialised trolley for collecting and transporting coolant from CNC machines. Sealed tank prevents spillage.',
      features: [
        'Sealed MS tank body — no spill design',
        'Drain valve for easy emptying',
        'Capacity markings on side',
        '4 swivel castors for manoeuvrability',
        'Stainless steel option for food/pharma',
        'Pump attachment port available'
      ],
      specs: [
        ['Tank Capacity', '50 – 200 litres'],
        ['Material', 'MS / SS304'],
        ['Drain Valve', '1-inch ball valve'],
        ['Castors', '4 × Ø100 swivel']
      ],
      applications: 'CNC machine shops, grinding operations, metalworking facilities, coolant recycling systems'
    },
    {
      id: 'five-shelf-trolley',
      name: 'Five Shelf Trolley',
      img: 'https://kotibhaskar.in/images/slideshow/42.png',
      desc: 'Five-level shelf trolley for moving large quantities of small items, finished goods, or loose components between departments.',
      features: [
        '5 shelves — maximises vertical storage during transit',
        'MS angle frame, powder-coated',
        'Full-perimeter side rails on each shelf',
        '4 swivel castors — 2 with brake',
        'Handle on each end',
        'Modular shelf pitch adjustment'
      ],
      specs: [
        ['Capacity', '250 – 400 kg total'],
        ['Shelf Size', '750×450 / 900×600 mm'],
        ['No. of Shelves', '5'],
        ['Overall Height', '1500 – 1700 mm'],
        ['Castor', '100×32 mm PU swivel']
      ],
      applications: 'Garment industry, pharma dispensing, food packaging, component kitting, hospitality trolleys'
    },
    {
      id: 'furnace-trolley',
      name: 'Furnace Trolley',
      img: 'https://kotibhaskar.in/images/slideshow/18.png',
      desc: 'High-temperature resistance trolley for loading and unloading furnaces and heat treatment chambers. Built to withstand extreme thermal environments.',
      features: [
        'MS or CI plate platform for high-temp service',
        'Low profile for furnace entry',
        'CI / forged steel wheels or rails',
        'No rubber components — all metal construction',
        'Custom dimensions to match furnace opening',
        'Optional: rail-guided track system'
      ],
      specs: [
        ['Max Temperature', '800°C (standard), 1000°C+ (special)'],
        ['Capacity', '500 – 5000 kg'],
        ['Platform Material', 'MS plate / Refractory lined'],
        ['Wheels', 'Cast iron flange wheels on rail'],
        ['Custom', 'Yes — designed to furnace dimensions']
      ],
      applications: 'Heat treatment furnaces, normalising, tempering, sintering, ceramic kilns, foundry operations'
    },
    {
      id: 'double-wheel-barrow',
      name: 'Double Wheel Barrow',
      img: 'https://kotibhaskar.in/images/slideshow/32.png',
      desc: 'Stable twin-wheel barrow for moving loose materials — sand, gravel, soil, chemicals — in rough terrain or on uneven surfaces.',
      features: [
        'Twin wheels for balance — no tipping',
        'Pneumatic tyre options for outdoor use',
        'MS tub body — heavy gauge',
        'Ergonomic tubular handle',
        'Powder-coated or galvanised finish',
        'Capacity markings on tub'
      ],
      specs: [
        ['Capacity', '150 – 200 kg'],
        ['Volume', '80 – 120 litres'],
        ['Wheel Type', 'Pneumatic / solid rubber'],
        ['Frame', 'MS tubular'],
        ['Finish', 'Powder coat / galvanised']
      ],
      applications: 'Construction sites, agriculture, outdoor landscaping, sand & gravel movement, composting yards'
    }
  ],

  /* ---- CATEGORY 3: Wheels & Castors ---- */
  wheels: [
    {
      id: 'uhmw-pe-wheels',
      name: 'UHMW-PE Wheels',
      img: 'https://kotibhaskar.in/images/castors/index/1.jpg',
      desc: 'Ultra High Molecular Weight Polyethylene wheels — compression moulded from virgin UHMW-PE powder. Floor-friendly, chemical resistant, and high impact strength.',
      features: [
        'Virgin UHMW-PE — white colour, high density',
        'High load carrying capacity',
        'High impact strength — no cracking under shock loads',
        'Low rolling & starting friction',
        'Does not damage floors — ideal for polished/epoxy floors',
        'Hardness: ~75 Shore D',
        'Excellent wear resistance',
        'Resistant to oil, grease, and chemicals',
        'Max working temperature: 70°C',
        'Ball bearing (BB) and plain bore (PLB) versions'
      ],
      specs: [
        ['Sizes (D×W mm)', '50×25 to 300×75 mm'],
        ['Bore ID', '12 to 25 mm'],
        ['Load Capacity', '60 to 1500 kg per wheel'],
        ['Bearing Options', 'Plain bore / 6001 / 6202 / 6004 / 6205'],
        ['Hardness', '~75 Shore D'],
        ['Colour', 'White / natural'],
        ['Max Temperature', '70°C']
      ],
      applications: 'Trolleys, conveyors, furniture, food industry, clean-rooms, pharmaceutical carts, hospital equipment'
    },
    {
      id: 'pu-ci-wheels',
      name: 'PU-CI Wheels (Polyurethane Cast Iron)',
      img: 'https://kotibhaskar.in/images/castors/index/2.jpg',
      desc: 'Cast iron core wheels moulded with polyurethane tread. Combines the strength of cast iron with the floor-protection and noise-reduction of polyurethane.',
      features: [
        'Cast iron hub — high load strength',
        'PU tread — floor friendly, low noise',
        'Shore hardness: 80–95 Shore A (PU)',
        'Good resistance to oils, chemicals, solvents',
        'Available with plain bore or ball bearing',
        'Low rolling resistance',
        'Suitable for smooth concrete and resin floors',
        'Does not leave black marks on floors'
      ],
      specs: [
        ['Sizes (D×W mm)', '80×25 to 250×60 mm'],
        ['Load Capacity', '150 to 2000 kg per wheel'],
        ['PU Tread Hardness', '80 – 95 Shore A'],
        ['Hub Material', 'Cast Iron (CI)'],
        ['Bore ID', '15 to 30 mm'],
        ['Bearing', 'Plain bore / Ball bearing available']
      ],
      applications: 'Industrial trolleys, heavy-duty carts, conveyors, warehouse equipment, tooling trolleys'
    },
    {
      id: 'cast-iron-wheels',
      name: 'Cast Iron Wheels',
      img: 'https://kotibhaskar.in/images/castors/index/3.jpg',
      desc: 'Solid cast iron wheels for high-temperature environments, heavy loads, and harsh conditions where non-metallic wheels would fail.',
      features: [
        'Solid cast iron construction — maximum durability',
        'Suitable for elevated temperatures (up to 250°C)',
        'Excellent resistance to solvents and chemicals',
        'High static and dynamic load capacity',
        'No deterioration in hot environments',
        'Available with plain bore or needle bearings',
        'Ideal for rail-guided furnace trolleys'
      ],
      specs: [
        ['Sizes (D×W mm)', '80×25 to 300×80 mm'],
        ['Load Capacity', '200 to 3000 kg per wheel'],
        ['Max Temperature', '250°C (standard)'],
        ['Material', 'Grade FG200 / FG260 cast iron'],
        ['Bore ID', '15 to 40 mm'],
        ['Bearing', 'Plain bore / Needle bearing']
      ],
      applications: 'Furnace trolleys, foundry, forging shops, heat treatment, outdoor industrial equipment, rail tracks'
    },
    {
      id: 'ms-solid-track-wheels',
      name: 'MS Solid Track Wheels',
      img: 'https://kotibhaskar.in/images/castors/index/4.jpg',
      desc: 'Mild steel solid wheels for rail-guided trolleys and material handling carts on flat track or angle iron rails.',
      features: [
        'Machined MS solid wheel body',
        'Flange or flat profile for rail guidance',
        'Precision bored centre — tight tolerance',
        'Hardened running surface option',
        'Available with plain bore or press-fit bearing',
        'Custom flange depth and rail profile matching'
      ],
      specs: [
        ['Sizes (D×W mm)', '80×20 to 250×60 mm'],
        ['Load Capacity', '200 to 2000 kg per wheel'],
        ['Material', 'Mild steel / EN8 hardened'],
        ['Flange Type', 'Single / double flange / flanged'],
        ['Bore ID', '15 to 40 mm'],
        ['Surface Treatment', 'Black / painted / zinc plated']
      ],
      applications: 'Rail-guided trolleys, conveyors on angle iron, furnace trolleys, transfer cars, assembly track systems'
    },
    {
      id: 'md-steel-castors',
      name: 'MD Steel Castors (Medium Duty)',
      img: 'https://kotibhaskar.in/images/castors/index/5.jpg',
      desc: 'Medium duty pressed steel castors for industrial trolleys, shop carts, and light industrial equipment. Most widely used castor for loads up to 250 kg.',
      features: [
        'Pressed steel housing — rigid and compact',
        'Top plate or stem mounting options',
        'Wheel options: PU, nylon, rubber, rubber-on-cast-iron',
        'Ball bearing swivel with double ball race',
        'Brake version available (brake on swivel)',
        'Corrosion protected — zinc plated or powder-coated'
      ],
      specs: [
        ['Load Capacity', '70 – 250 kg per castor'],
        ['Wheel Diameter', '75 – 125 mm'],
        ['Plate Size', '95×70 to 105×80 mm'],
        ['Stem Options', 'M10/M12 threaded / grip ring stem'],
        ['Swivel Radius', '65 – 85 mm'],
        ['Wheel Material', 'PU / Nylon / Rubber / RDCI']
      ],
      applications: 'Workshop trolleys, hospital equipment, platform trolleys, shelving, commercial carts'
    },
    {
      id: 'mhd-castors',
      name: 'MHD Castors (Medium Heavy Duty)',
      img: 'https://kotibhaskar.in/images/castors/index/6.jpg',
      desc: 'Medium-heavy duty castors with reinforced swivel housing for loads between 250–600 kg. Suitable for industrial trolleys and equipment.',
      features: [
        'Reinforced steel housing — thicker gauge than MD',
        'Double ball race swivel — smooth 360° rotation',
        'Precision machined axle bolt',
        'Wheel options: PU, nylon, rubber, PU-CI',
        'Brake version: integrated foot brake',
        'Top plate and bolt hole pattern options'
      ],
      specs: [
        ['Load Capacity', '250 – 600 kg per castor'],
        ['Wheel Diameter', '100 – 160 mm'],
        ['Plate Size', '120×85 to 140×110 mm'],
        ['Swivel Radius', '90 – 110 mm'],
        ['Wheel Material', 'PU / Rubber / PU-CI'],
        ['Finish', 'Zinc plated / powder-coated']
      ],
      applications: 'Heavy trolleys, industrial carts, AGV wheels, automotive jigs, engineering equipment'
    },
    {
      id: 'heavy-duty-castors',
      name: 'Heavy Duty Castors',
      img: 'https://kotibhaskar.in/images/castors/index/7.jpg',
      desc: 'Heavy-duty industrial castors for loads up to 2000 kg per castor. Used on transfer cars, heavy equipment, and large industrial trolleys.',
      features: [
        'Forged or heavy-gauge fabricated housing',
        'Kingpin design for high radial load transfer',
        'Precision taper roller or ball bearing swivel',
        'Wheel options: PU, CI, rubber, nylon, welded steel',
        'Available: fixed and swivel configurations',
        'Top plate with reinforced bolt pattern',
        'Corrosion protection: zinc, paint, or hot-dip galvanised'
      ],
      specs: [
        ['Load Capacity', '600 – 2000 kg per castor'],
        ['Wheel Diameter', '150 – 250 mm'],
        ['Plate Size', '150×110 to 200×160 mm'],
        ['Wheel Width', '50 – 80 mm'],
        ['Bearing', 'Taper roller / ball bearing'],
        ['Wheel Material', 'PU / CI / welded MS / nylon']
      ],
      applications: 'Transfer cars, assembly jigs, heavy tooling, press tool trolleys, shipyards, steel mills'
    },
    {
      id: 'hd-twin-castors',
      name: 'HD Twin Castors (Heavy Duty Twin)',
      img: 'https://kotibhaskar.in/images/castors/index/8.jpg',
      desc: 'Twin-wheel heavy duty castors that distribute load across two wheels for better stability and lower floor pressure. Ideal for very heavy loads on sensitive floors.',
      features: [
        'Twin wheel design — doubles load distribution',
        'Lower floor contact pressure vs single wheel',
        'Better stability under dynamic loads',
        'Forged / heavy fabricated housing',
        'Precision bearing swivel head',
        'Wheel options: PU, rubber, nylon, CI',
        'Foot brake and total lock options'
      ],
      specs: [
        ['Load Capacity', '800 – 4000 kg per castor'],
        ['Wheel Diameter', '125 – 200 mm per wheel'],
        ['Total Castor Width', '130 – 220 mm'],
        ['Plate Size', '160×120 to 220×180 mm'],
        ['Wheel Material', 'PU / rubber / nylon / CI'],
        ['Swivel Bearing', 'Precision ball or taper roller']
      ],
      applications: 'Very heavy trolleys, transfer cars, aircraft ground support, heavy jigs, die-handling equipment'
    }
  ]
};

/* ============================================================
   KEYWORD → PRODUCT SEARCH MAP (for smart finder)
   ============================================================ */
const KEYWORD_MAP = [
  { words: ['pallet','euro pallet','loaded pallet'], ids: ['hydraulic-pallet-truck','electric-pallet-truck'] },
  { words: ['stack','stacker','racking','height','mezzanine load'], ids: ['manual-stacker','electric-stacker'] },
  { words: ['drum','barrel','200l','oil drum'], ids: ['hydraulic-drum-tilter','electric-drum-tilter','manual-drum-gripper','electric-drum-gripper','drum-trolley'] },
  { words: ['crane','lift engine','heavy lift','motor','pump'], ids: ['hydraulic-floor-crane','electric-floor-crane','jib-crane','gantry'] },
  { words: ['conveyor','roller','belt','production line'], ids: ['gravity-roller-conveyor','belt-conveyor'] },
  { words: ['shelf','shelving','storage rack','bin'], ids: ['industrial-shelving','shelf-trolley','bin-trolley','five-shelf-trolley'] },
  { words: ['dock','truck','loading bay'], ids: ['dock-leveller'] },
  { words: ['scissor','ergo','work height','positioning'], ids: ['scissor-lift'] },
  { words: ['platform trolley','flat trolley','boxes','bags','crates'], ids: ['platform-trolley'] },
  { words: ['workshop','tool','cnc','machine'], ids: ['workshop-trolley','cnc-tool-trolley','chip-trolley','coolant-trolley'] },
  { words: ['gas','cylinder','welding','oxygen'], ids: ['gas-cylinder-trolley'] },
  { words: ['chip','swarf','scrap'], ids: ['chip-trolley'] },
  { words: ['furnace','heat treatment','high temp','oven'], ids: ['furnace-trolley','cast-iron-wheels'] },
  { words: ['uhmw','polyethylene','pe wheel','light trolley','clean','hospital','pharma'], ids: ['uhmw-pe-wheels'] },
  { words: ['pu','polyurethane','quiet','floor friendly','epoxy','resin floor'], ids: ['pu-ci-wheels','md-steel-castors','mhd-castors'] },
  { words: ['cast iron','ci wheel','rough','outdoor','chemical'], ids: ['cast-iron-wheels'] },
  { words: ['ms wheel','rail','track','guided'], ids: ['ms-solid-track-wheels'] },
  { words: ['castor','caster','swivel','medium duty'], ids: ['md-steel-castors','mhd-castors'] },
  { words: ['heavy duty castor','heavy castor','2000kg','transfer car'], ids: ['heavy-duty-castors','hd-twin-castors'] },
  { words: ['twin','twin castor','large load','floor pressure'], ids: ['hd-twin-castors'] },
  { words: ['warehouse','godown','logistics','distribution','move material','material movement'], ids: ['hydraulic-pallet-truck','platform-trolley','electric-pallet-truck','shelf-trolley'] },
  { words: ['wheel','wheels'], ids: ['uhmw-pe-wheels','pu-ci-wheels','cast-iron-wheels','ms-solid-track-wheels'] },
  { words: ['heavy load','heavy weight','tonnes'], ids: ['heavy-duty-castors','hd-twin-castors','hydraulic-pallet-truck','electric-stacker'] },
  { words: ['goods lift','mezzanine','floor level'], ids: ['goods-lift'] },
  { words: ['steel pallet','iron pallet','metal pallet'], ids: ['steel-pallet'] }
];

/* ============================================================
   UTILITIES
   ============================================================ */
function getAllProducts() {
  return [...PRODUCTS.mhe, ...PRODUCTS.trolleys, ...PRODUCTS.wheels];
}

function findProductById(id) {
  return getAllProducts().find(p => p.id === id) || null;
}

/* ============================================================
   TAB SWITCHING — THE CORE FIX
   ============================================================ */
function showCat(catKey) {
  // Update active tab styling
  document.querySelectorAll('.cat-tab').forEach(el => {
    el.classList.remove('active');
    el.style.background = '';
    el.style.border = '';
  });
  const activeTab = document.querySelector(`[data-cat="${catKey}"]`);
  if (activeTab) {
    activeTab.classList.add('active');
    activeTab.style.background = '#fff8f0';
    activeTab.style.border = '2px solid #e87722';
  }

  // Render product grid
  const grid = document.getElementById('product-grid');
  if (!grid) { console.error('product-grid element not found'); return; }

  const prods = PRODUCTS[catKey] || [];
  grid.innerHTML = prods.map(p => `
    <div class="prod-card" onclick="openModal('${p.id}')" style="
      background:#fff; border:1px solid #e8e0d4; border-radius:6px;
      padding:12px; cursor:pointer; display:flex; flex-direction:column;
      align-items:center; gap:8px; transition:box-shadow 0.2s, transform 0.2s;
    "
    onmouseenter="this.style.boxShadow='0 4px 16px rgba(232,119,34,0.18)'; this.style.transform='translateY(-3px)'"
    onmouseleave="this.style.boxShadow=''; this.style.transform=''"
    >
      <div style="width:100%; height:160px; overflow:hidden; display:flex; align-items:center; justify-content:center; background:#f8f4ee; border-radius:4px;">
        <img src="${p.img}" alt="${p.name}" style="max-width:100%; max-height:150px; object-fit:contain;"
          onerror="this.src='https://via.placeholder.com/200x150?text=Image+Loading'; this.onerror=null"/>
      </div>
      <p style="font-family:'Barlow Condensed',sans-serif; font-size:13px; font-weight:700; text-transform:uppercase; letter-spacing:0.5px; color:#1a2340; text-align:center; margin:0; line-height:1.3;">${p.name}</p>
      <span style="font-size:11px; color:#e87722; font-weight:600;">→ Specs</span>
    </div>
  `).join('');
}

/* ============================================================
   PRODUCT MODAL
   ============================================================ */
function openModal(productId) {
  const p = findProductById(productId);
  if (!p) { console.error('Product not found:', productId); return; }

  // Remove existing modal if any
  const existing = document.getElementById('kb-product-modal');
  if (existing) existing.remove();

  const modal = document.createElement('div');
  modal.id = 'kb-product-modal';
  modal.style.cssText = `
    position:fixed; inset:0; background:rgba(0,0,0,0.65); z-index:99999;
    display:flex; align-items:flex-start; justify-content:center;
    padding:20px; overflow-y:auto;
  `;

  const specsRows = p.specs.map(([k, v]) => `
    <tr>
      <td style="padding:8px 12px; font-weight:600; color:#1a2340; background:#f5f0e8; border:1px solid #e0d8cc; white-space:nowrap;">${k}</td>
      <td style="padding:8px 12px; color:#444; border:1px solid #e0d8cc;">${v}</td>
    </tr>
  `).join('');

  const featuresHtml = p.features.map(f => `
    <li style="margin-bottom:6px; padding-left:4px;">${f}</li>
  `).join('');

  modal.innerHTML = `
    <div style="
      background:#fff; border-radius:10px; max-width:800px; width:100%;
      box-shadow:0 20px 60px rgba(0,0,0,0.35); position:relative;
      font-family:'Barlow',sans-serif; margin:auto;
    ">
      <!-- Header -->
      <div style="background:#1a2340; color:#fff; padding:20px 24px; border-radius:10px 10px 0 0; display:flex; justify-content:space-between; align-items:center;">
        <div>
          <p style="margin:0; font-size:11px; color:#e87722; font-weight:700; text-transform:uppercase; letter-spacing:1px;">KOTIBHASKAR INDUSTRIES</p>
          <h2 style="margin:4px 0 0; font-size:22px; font-weight:800; font-family:'Barlow Condensed',sans-serif; text-transform:uppercase;">${p.name}</h2>
        </div>
        <button onclick="document.getElementById('kb-product-modal').remove()"
          style="background:rgba(255,255,255,0.15); border:none; color:#fff; font-size:22px; cursor:pointer; width:36px; height:36px; border-radius:50%; display:flex; align-items:center; justify-content:center; flex-shrink:0;">×</button>
      </div>

      <!-- Action buttons -->
      <div style="background:#f5f0e8; padding:12px 24px; display:flex; gap:12px; flex-wrap:wrap; border-bottom:1px solid #e0d8cc;">
        <button onclick="printProductPDF('${p.id}')"
          style="background:#1a2340; color:#fff; border:none; padding:10px 18px; border-radius:5px; cursor:pointer; font-size:13px; font-weight:600; display:flex; align-items:center; gap:6px;">
          🖶 Print as PDF
        </button>
        <button onclick="openEnquiry('${p.name}')"
          style="background:#e87722; color:#fff; border:none; padding:10px 18px; border-radius:5px; cursor:pointer; font-size:13px; font-weight:600; display:flex; align-items:center; gap:6px;">
          ✉ Send Enquiry
        </button>
      </div>

      <!-- Body -->
      <div style="padding:24px; display:grid; grid-template-columns:1fr 1fr; gap:24px;">
        <!-- Left: image + description -->
        <div>
          <div style="background:#f8f4ee; border-radius:6px; padding:16px; display:flex; align-items:center; justify-content:center; min-height:220px; margin-bottom:16px;">
            <img src="${p.img}" alt="${p.name}" style="max-width:100%; max-height:220px; object-fit:contain;"
              onerror="this.src='https://via.placeholder.com/280x220?text=Product+Image'"/>
          </div>
          <h3 style="font-size:13px; text-transform:uppercase; letter-spacing:1px; color:#e87722; font-weight:700; margin:0 0 8px;">Description</h3>
          <p style="font-size:14px; color:#444; line-height:1.6; margin:0 0 16px;">${p.desc}</p>
          <h3 style="font-size:13px; text-transform:uppercase; letter-spacing:1px; color:#e87722; font-weight:700; margin:0 0 8px;">Applications</h3>
          <p style="font-size:14px; color:#444; line-height:1.6; margin:0;">${p.applications}</p>
        </div>
        <!-- Right: features + specs -->
        <div>
          <h3 style="font-size:13px; text-transform:uppercase; letter-spacing:1px; color:#e87722; font-weight:700; margin:0 0 10px;">Key Features</h3>
          <ul style="font-size:13px; color:#444; line-height:1.7; padding-left:18px; margin:0 0 20px;">
            ${featuresHtml}
          </ul>
          <h3 style="font-size:13px; text-transform:uppercase; letter-spacing:1px; color:#e87722; font-weight:700; margin:0 0 10px;">Specifications</h3>
          <table style="width:100%; border-collapse:collapse; font-size:13px;">
            ${specsRows}
          </table>
        </div>
      </div>

      <!-- Footer -->
      <div style="background:#f5f0e8; padding:12px 24px; border-radius:0 0 10px 10px; text-align:center; border-top:1px solid #e0d8cc;">
        <p style="margin:0; font-size:12px; color:#666;">Custom variants available. Contact: <strong>amodsales@gmail.com</strong> | <strong>+91 98224 13252</strong></p>
      </div>
    </div>
  `;

  // Close on backdrop click
  modal.addEventListener('click', (e) => {
    if (e.target === modal) modal.remove();
  });

  document.body.appendChild(modal);
}

/* ============================================================
   PRINT AS PDF — Clean datasheet
   ============================================================ */
function printProductPDF(productId) {
  const p = findProductById(productId);
  if (!p) return;

  const specsRows = p.specs.map(([k, v]) => `
    <tr>
      <td style="padding:6px 10px; font-weight:600; color:#000; background:#f5f5f5; border:1px solid #ccc; width:40%;">${k}</td>
      <td style="padding:6px 10px; color:#222; border:1px solid #ccc;">${v}</td>
    </tr>
  `).join('');

  const featuresHtml = p.features.map(f => `<li style="margin-bottom:4px;">${f}</li>`).join('');

  const printWindow = window.open('', '_blank', 'width=900,height=700');
  printWindow.document.write(`<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <title>${p.name} — Kotibhaskar Industries</title>
  <style>
    * { margin:0; padding:0; box-sizing:border-box; }
    body { font-family: Arial, Helvetica, sans-serif; font-size:13px; color:#000; background:#fff; }
    @page { margin: 15mm 15mm 15mm 15mm; size: A4; }
    @media print {
      .no-print { display:none !important; }
      body { -webkit-print-color-adjust: exact; print-color-adjust: exact; }
    }
    .page { padding:20px; max-width:800px; margin:0 auto; }
    .header { display:flex; justify-content:space-between; align-items:center; border-bottom:3px solid #000; padding-bottom:12px; margin-bottom:16px; }
    .company-name { font-size:22px; font-weight:900; letter-spacing:1px; text-transform:uppercase; }
    .company-sub { font-size:10px; color:#555; margin-top:3px; }
    .product-title { font-size:20px; font-weight:900; text-transform:uppercase; border-bottom:2px solid #000; padding-bottom:8px; margin-bottom:16px; }
    .grid { display:grid; grid-template-columns:240px 1fr; gap:20px; margin-bottom:16px; }
    .img-box { text-align:center; border:1px solid #ddd; padding:12px; border-radius:4px; }
    .img-box img { max-width:100%; max-height:200px; object-fit:contain; }
    .section-title { font-size:11px; font-weight:700; text-transform:uppercase; letter-spacing:1px; color:#000; background:#eee; padding:5px 8px; margin:12px 0 6px; border-left:4px solid #000; }
    .desc { font-size:13px; line-height:1.6; color:#222; }
    ul { padding-left:16px; }
    li { margin-bottom:3px; font-size:12px; }
    table { width:100%; border-collapse:collapse; font-size:12px; }
    .applications { font-size:12px; color:#333; line-height:1.5; }
    .footer { border-top:2px solid #000; padding-top:10px; margin-top:20px; display:flex; justify-content:space-between; font-size:10px; color:#555; }
    .print-btn { position:fixed; top:15px; right:15px; padding:10px 20px; background:#000; color:#fff; border:none; font-size:14px; cursor:pointer; border-radius:4px; font-weight:700; z-index:9999; }
  </style>
</head>
<body>
  <button class="print-btn no-print" onclick="window.print()">⊞ Print / Save PDF</button>
  <div class="page">
    <div class="header">
      <div>
        <div class="company-name">KOTIBHASKAR INDUSTRIES</div>
        <div class="company-sub">Plot No. K-3/2/1, Addl. MIDC, Satara, Maharashtra | amodsales@gmail.com | +91 98224 13252</div>
      </div>
      <div style="font-size:10px; text-align:right; color:#555;">
        PRODUCT DATASHEET<br>${new Date().toLocaleDateString('en-IN')}
      </div>
    </div>

    <div class="product-title">${p.name}</div>

    <div class="grid">
      <div>
        <div class="img-box">
          <img src="${p.img}" alt="${p.name}" onerror="this.alt='Image unavailable'"/>
        </div>
        <div class="section-title">Description</div>
        <p class="desc">${p.desc}</p>
        <div class="section-title">Applications</div>
        <p class="applications">${p.applications}</p>
      </div>
      <div>
        <div class="section-title">Key Features</div>
        <ul>${featuresHtml}</ul>
        <div class="section-title">Technical Specifications</div>
        <table>${specsRows}</table>
        <p style="font-size:10px; color:#777; margin-top:8px;">* Specifications subject to change. Custom variants available on request.</p>
      </div>
    </div>

    <div class="footer">
      <span>Kotibhaskar Industries, Satara, Maharashtra, India | kotibhaskarindustries.com</span>
      <span>amodsales@gmail.com | amodsatara@gmail.com | +91 83800 95804</span>
    </div>
  </div>
</body>
</html>`);
  printWindow.document.close();
}

/* ============================================================
   ENQUIRY — opens form and pre-fills product name
   ============================================================ */
function openEnquiry(productName) {
  // Close the modal
  const modal = document.getElementById('kb-product-modal');
  if (modal) modal.remove();

  // Scroll to contact section
  const contactSection = document.getElementById('contact') || document.querySelector('#contact, [id*="contact"], [id*="enquiry"]');
  if (contactSection) {
    contactSection.scrollIntoView({ behavior: 'smooth' });
  }

  // Pre-fill product field (try common field IDs/names)
  setTimeout(() => {
    const productFields = [
      document.querySelector('select[name="product"], select[id*="product"]'),
      document.querySelector('input[name="product"], input[id*="product"]'),
      document.querySelector('textarea[name="requirement"], textarea[id*="requirement"]')
    ].filter(Boolean);

    productFields.forEach(field => {
      if (field.tagName === 'SELECT') {
        // Find matching option or first option
        const opt = Array.from(field.options).find(o => o.text.toLowerCase().includes(productName.toLowerCase().substring(0,5)));
        if (opt) field.value = opt.value;
      } else {
        field.value = productName;
      }
    });

    // Also try to fill the message field
    const msgField = document.querySelector('textarea[name="message"], textarea[id*="message"], textarea[id*="requirement"]');
    if (msgField && !msgField.value) {
      msgField.value = `I am interested in: ${productName}\n\nPlease provide more information and a quotation.`;
    }
  }, 600);
}

/* ============================================================
   SMART PRODUCT FINDER — keyword matching
   ============================================================ */
function initSmartFinder() {
  const input = document.querySelector('input[placeholder*="product"], input[placeholder*="requirement"], input[placeholder*="describe"], #finder-input');
  if (!input) return;

  // Create results dropdown
  const resultsDiv = document.createElement('div');
  resultsDiv.id = 'finder-results';
  resultsDiv.style.cssText = `
    position:absolute; background:#fff; border:1px solid #e0d8cc;
    border-radius:6px; box-shadow:0 8px 24px rgba(0,0,0,0.12);
    z-index:1000; max-height:320px; overflow-y:auto;
    width:100%; display:none; top:100%; left:0; margin-top:4px;
  `;
  input.parentElement.style.position = 'relative';
  input.parentElement.appendChild(resultsDiv);

  function search(query) {
    query = query.toLowerCase().trim();
    if (query.length < 2) { resultsDiv.style.display = 'none'; return; }

    // Keyword-based lookup
    const matchedIds = new Set();
    KEYWORD_MAP.forEach(({ words, ids }) => {
      if (words.some(w => query.includes(w) || w.includes(query))) {
        ids.forEach(id => matchedIds.add(id));
      }
    });

    // Also search by product name
    getAllProducts().forEach(p => {
      if (p.name.toLowerCase().includes(query) || p.desc.toLowerCase().includes(query)) {
        matchedIds.add(p.id);
      }
    });

    const matches = [...matchedIds].map(id => findProductById(id)).filter(Boolean);

    if (matches.length === 0) {
      resultsDiv.innerHTML = `<div style="padding:12px 16px; color:#666; font-size:13px;">No exact match — try: pallet, stacker, drum, crane, trolley, wheel, castor</div>`;
      resultsDiv.style.display = 'block';
      return;
    }

    resultsDiv.innerHTML = `
      <div style="padding:8px 12px; background:#f5f0e8; font-size:11px; font-weight:700; color:#e87722; text-transform:uppercase; letter-spacing:0.5px; border-bottom:1px solid #e0d8cc;">
        ${matches.length} product${matches.length>1?'s':''} found
      </div>
      ${matches.map(p => `
        <div onclick="openModal('${p.id}'); document.getElementById('finder-results').style.display='none';"
          style="display:flex; align-items:center; gap:12px; padding:10px 12px; cursor:pointer; border-bottom:1px solid #f0ede8; transition:background 0.15s;"
          onmouseenter="this.style.background='#fff8f0'" onmouseleave="this.style.background='#fff'"
        >
          <img src="${p.img}" style="width:44px; height:44px; object-fit:contain; flex-shrink:0; background:#f8f4ee; border-radius:4px; padding:3px;"
            onerror="this.src='https://via.placeholder.com/44x44?text=?'"/>
          <div>
            <div style="font-size:13px; font-weight:700; color:#1a2340; font-family:'Barlow Condensed',sans-serif; text-transform:uppercase;">${p.name}</div>
            <div style="font-size:11px; color:#666; line-height:1.4;">${p.desc.substring(0,80)}…</div>
          </div>
        </div>
      `).join('')}
    `;
    resultsDiv.style.display = 'block';
  }

  input.addEventListener('input', () => search(input.value));
  input.addEventListener('keydown', (e) => { if (e.key === 'Enter') search(input.value); });

  // Close on outside click
  document.addEventListener('click', (e) => {
    if (!input.parentElement.contains(e.target)) {
      resultsDiv.style.display = 'none';
    }
  });

  // Also wire up GO/Search button
  const goBtn = input.parentElement.querySelector('button') || input.nextElementSibling;
  if (goBtn && (goBtn.tagName === 'BUTTON' || goBtn.tagName === 'A')) {
    goBtn.addEventListener('click', () => search(input.value));
  }
}

/* ============================================================
   OUR STORY — fix contrast
   ============================================================ */
function fixOurStory() {
  // Try multiple possible selectors
  const storySelectors = ['#about', '.story-section', '[id*="story"]', '[class*="story"]', 'section:has(h2)'];
  let storyEl = null;
  for (const sel of storySelectors) {
    try {
      const els = document.querySelectorAll(sel);
      els.forEach(el => {
        const text = el.textContent;
        if (text.includes('Our Story') || text.includes('25 Years') || text.includes('Engineering Trust')) {
          storyEl = el;
        }
      });
    } catch(e) {}
  }

  if (storyEl) {
    // Fix any text with poor contrast
    storyEl.querySelectorAll('p, li, span, h2, h3, h4').forEach(el => {
      const bg = window.getComputedStyle(el).backgroundColor;
      const col = window.getComputedStyle(el).color;
      // If text appears invisible (white on white / dark on dark), force black
      el.style.color = '#222';
    });
  }

  // Generic: scan entire page for invisible text
  document.querySelectorAll('p, li, span').forEach(el => {
    const computed = window.getComputedStyle(el);
    const color = computed.color;
    const bg = computed.backgroundColor;
    // crude: if color is near white (255,255,255) override
    if (color === 'rgb(255, 255, 255)' || color === 'rgba(255, 255, 255, 1)') {
      // check if parent background is also light
      const parentBg = window.getComputedStyle(el.parentElement || document.body).backgroundColor;
      if (parentBg && (parentBg.includes('255, 255, 255') || parentBg.includes('248,') || parentBg.includes('245,'))) {
        el.style.color = '#1a2340';
      }
    }
  });
}

/* ============================================================
   REMOVE MANUFACTURING FACILITY
   ============================================================ */
function removeManufacturingSection() {
  const candidates = document.querySelectorAll('section, div');
  candidates.forEach(el => {
    const text = el.textContent || '';
    const h = el.querySelector('h2, h3, h4');
    if (h && (
      h.textContent.includes('Production Facilities') ||
      h.textContent.includes('Manufacturing Facility') ||
      h.textContent.includes('Our Plant')
    )) {
      el.remove();
    }
  });

  // Remove nav links to facility
  document.querySelectorAll('a[href*="facility"], a[href*="Facility"]').forEach(a => {
    const li = a.closest('li');
    if (li) li.remove();
    else a.remove();
  });
}

/* ============================================================
   WIRE UP EXISTING TAB BUTTONS
   ============================================================ */
function wireTabs() {
  // Look for the 3 category boxes/tabs in the existing HTML
  const allClickables = document.querySelectorAll('[onclick*="showCat"], .cat-tab, .product-category');
  // If already wired, nothing to do.

  // Find the tabs by text content
  document.querySelectorAll('.cat-tab, [class*="cat"], section .product-tab, [class*="tab"]').forEach(el => {
    const text = el.textContent.toLowerCase();
    if (text.includes('material handling trolley') || text.includes('trolleys')) {
      el.setAttribute('data-cat', 'trolleys');
      el.onclick = () => showCat('trolleys');
    } else if (text.includes('wheel') || text.includes('castor')) {
      el.setAttribute('data-cat', 'wheels');
      el.onclick = () => showCat('wheels');
    } else if (text.includes('material handling equipment') || text.includes('equipment')) {
      el.setAttribute('data-cat', 'mhe');
      el.onclick = () => showCat('mhe');
    }
  });

  // Also wire by onclick string patterns already in HTML
  document.querySelectorAll('[onclick]').forEach(el => {
    const oc = el.getAttribute('onclick') || '';
    if (oc.includes("showCat('trolleys')") || oc.includes('showCat("trolleys")')) {
      el.setAttribute('data-cat', 'trolleys');
      el.onclick = () => showCat('trolleys');
    } else if (oc.includes("showCat('wheels')") || oc.includes('showCat("wheels")')) {
      el.setAttribute('data-cat', 'wheels');
      el.onclick = () => showCat('wheels');
    } else if (oc.includes("showCat('mhe')") || oc.includes('showCat("mhe")')) {
      el.setAttribute('data-cat', 'mhe');
      el.onclick = () => showCat('mhe');
    }
  });
}

/* ============================================================
   EMAILJS INTEGRATION
   ============================================================ */
function initEmailJS() {
  if (EMAILJS_PUBLIC_KEY === 'YOUR_PUBLIC_KEY') {
    console.warn('[Kotibhaskar Patch] EmailJS not configured. Replace EMAILJS_SERVICE_ID, EMAILJS_TEMPLATE_ID, EMAILJS_PUBLIC_KEY at the top of kotibhaskar-patch.js');
    return;
  }

  // Load EmailJS SDK
  const script = document.createElement('script');
  script.src = 'https://cdn.jsdelivr.net/npm/@emailjs/browser@4/dist/email.min.js';
  script.onload = () => {
    emailjs.init(EMAILJS_PUBLIC_KEY);
    console.log('[Kotibhaskar Patch] EmailJS initialised.');
    hookEnquiryForm();
  };
  document.head.appendChild(script);
}

function hookEnquiryForm() {
  const form = document.querySelector('form, [id*="enquiry-form"], [class*="enquiry"]');
  if (!form) return;

  form.addEventListener('submit', (e) => {
    e.preventDefault();

    const data = {
      from_name:    (form.querySelector('[name="name"], [id*="name"]') || {}).value || '',
      company:      (form.querySelector('[name="company"], [id*="company"]') || {}).value || '',
      phone:        (form.querySelector('[name="phone"], [id*="phone"]') || {}).value || '',
      reply_to:     (form.querySelector('[name="email"], [id*="email"]') || {}).value || '',
      product:      (form.querySelector('[name="product"], [id*="product"], select') || {}).value || '',
      message:      (form.querySelector('[name="message"], textarea') || {}).value || '',
      to_email:     'amodsales@gmail.com'
    };

    const submitBtn = form.querySelector('[type="submit"], button');
    if (submitBtn) { submitBtn.disabled = true; submitBtn.textContent = 'Sending…'; }

    if (EMAILJS_PUBLIC_KEY !== 'YOUR_PUBLIC_KEY') {
      emailjs.send(EMAILJS_SERVICE_ID, EMAILJS_TEMPLATE_ID, data)
        .then(() => showSuccessMessage(form, submitBtn))
        .catch(err => {
          console.error('EmailJS error:', err);
          showErrorMessage(form, submitBtn);
        });
    } else {
      // Demo mode — just show success
      setTimeout(() => showSuccessMessage(form, submitBtn), 800);
    }
  });
}

function showSuccessMessage(form, btn) {
  if (btn) { btn.disabled = false; btn.textContent = 'Send Enquiry →'; }

  // Create success overlay
  const overlay = document.createElement('div');
  overlay.style.cssText = `
    position:fixed; inset:0; background:rgba(0,0,0,0.65); z-index:99999;
    display:flex; align-items:center; justify-content:center; padding:20px;
  `;
  overlay.innerHTML = `
    <div style="background:#fff; border-radius:12px; padding:40px; text-align:center; max-width:400px; box-shadow:0 20px 60px rgba(0,0,0,0.3);">
      <div style="font-size:48px; margin-bottom:16px;">✅</div>
      <h2 style="font-family:'Barlow Condensed',sans-serif; font-size:24px; font-weight:900; color:#1a2340; text-transform:uppercase; margin:0 0 12px;">Thank You!</h2>
      <p style="color:#555; font-size:15px; line-height:1.6; margin:0 0 20px;">Your enquiry has been received. Our team will contact you within 1 business day.</p>
      <button onclick="this.closest('[style*=fixed]').remove()" style="background:#e87722; color:#fff; border:none; padding:12px 24px; border-radius:6px; cursor:pointer; font-size:14px; font-weight:700;">Close</button>
    </div>
  `;
  document.body.appendChild(overlay);
  if (form) form.reset();
}

function showErrorMessage(form, btn) {
  if (btn) { btn.disabled = false; btn.textContent = 'Send Enquiry →'; }
  alert('There was an error sending the enquiry. Please email us directly at amodsales@gmail.com or call +91 98224 13252.');
}

/* ============================================================
   RESPONSIVE CSS INJECTION
   ============================================================ */
function injectResponsiveCSS() {
  const style = document.createElement('style');
  style.textContent = `
    /* ---- Product grid responsive ---- */
    #product-grid {
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
      gap: 16px;
    }
    @media (max-width: 1023px) {
      #product-grid {
        grid-template-columns: repeat(auto-fill, minmax(160px, 1fr));
        gap: 12px;
      }
    }
    @media (max-width: 767px) {
      #product-grid {
        grid-template-columns: repeat(2, 1fr);
        gap: 10px;
      }
      .prod-card img {
        max-height: 120px !important;
      }
    }
    @media (max-width: 479px) {
      #product-grid {
        grid-template-columns: repeat(2, 1fr);
        gap: 8px;
      }
    }

    /* ---- Modal responsive ---- */
    #kb-product-modal > div > div:nth-child(3) {
      display: grid;
      grid-template-columns: 1fr 1fr;
    }
    @media (max-width: 700px) {
      #kb-product-modal > div > div:nth-child(3) {
        grid-template-columns: 1fr !important;
      }
      #kb-product-modal > div {
        margin: 10px !important;
      }
    }

    /* ---- Category tabs ---- */
    .cat-tab { cursor: pointer; }
    .cat-tab.active {
      background: #fff8f0 !important;
      border: 2px solid #e87722 !important;
    }

    /* ---- Our Story visibility fix ---- */
    #about p, #about li, #about span,
    [id*="story"] p, [id*="story"] li,
    .story-content p, .story-text p {
      color: #222 !important;
    }
    #about h2, [id*="story"] h2 {
      color: #1a2340 !important;
    }

    /* ---- Get Quote button centred ---- */
    .get-quote-btn, [href*="#contact"], a[class*="quote"] {
      display: inline-flex;
      align-items: center;
      justify-content: center;
    }

    /* ---- No horizontal scroll ---- */
    body { overflow-x: hidden; }
    
    /* ---- Finder results position ---- */
    #finder-results { font-family: 'Barlow', sans-serif; }
  `;
  document.head.appendChild(style);
}

/* ============================================================
   INIT — run everything after DOM ready
   ============================================================ */
function init() {
  injectResponsiveCSS();
  wireTabs();
  removeManufacturingSection();
  fixOurStory();
  initSmartFinder();
  initEmailJS();

  // Show MHE tab by default (avoids blank grid)
  // Check which tab is currently active, if none — show mhe
  const activeTab = document.querySelector('.cat-tab.active, [style*="border: 2px solid"]');
  if (!activeTab) {
    showCat('mhe');
  }

  // Expose globals needed by existing HTML onclick attributes
  window.showCat   = showCat;
  window.openModal = openModal;
  window.printProductPDF = printProductPDF;
  window.openEnquiry = openEnquiry;
}

if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', init);
} else {
  init();
}
