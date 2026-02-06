#!/usr/bin/env node

/**
 * EVDB Data Validation Script
 * 
 * Validates vehicle content files against schema and checks for:
 * - Required fields
 * - Enum value compliance
 * - Data consistency
 * - Missing translations
 * - Image references
 */

const fs = require('fs');
const path = require('path');
const yaml = require('js-yaml');

// Load enums from schema
const ENUMS = {
  body_type: [
    'SEDAN', 'HATCHBACK', 'SUV', 'CROSSOVER', 'COUPE', 'CONVERTIBLE',
    'WAGON', 'VAN', 'PICKUP', 'MINIBUS', 'BUS', 'TRUCK', 'OTHER'
  ],
  battery_chemistry: ['LFP', 'NMC', 'NCA', 'LTO', 'SODIUM_ION', 'SOLID_STATE', 'OTHER'],
  drivetrain: ['FWD', 'RWD', 'AWD', '4WD'],
  charging_port_ac: ['TYPE1', 'TYPE2', 'OTHER'],
  charging_port_dc: ['CCS1', 'CCS2', 'CHADEMO', 'TESLA_NACS', 'TESLA_SCC', 'GB_T', 'OTHER'],
  dc_speed_class: ['NONE', 'SLOW', 'MEDIUM', 'FAST', 'ULTRA_FAST', 'HYPER_FAST'],
  market_status: ['available', 'discontinued', 'announced'],
  image_type: ['exterior', 'interior', 'technical', 'press', 'render', 'user']
};

const REQUIRED_FIELDS = ['title', 'manufacturer', 'body', 'segment'];
const RECOMMENDED_FIELDS = ['description', 'battery', 'range', 'performance', 'charging'];

const errors = [];
const warnings = [];

/**
 * Parse front matter from markdown file
 */
function parseFrontMatter(filePath) {
  const content = fs.readFileSync(filePath, 'utf8');
  const match = content.match(/^---\n([\s\S]*?)\n---/);
  
  if (!match) {
    return null;
  }
  
  try {
    return yaml.load(match[1]);
  } catch (e) {
    errors.push(`${filePath}: Invalid YAML in front matter - ${e.message}`);
    return null;
  }
}

/**
 * Validate required fields
 */
function validateRequiredFields(filePath, data) {
  for (const field of REQUIRED_FIELDS) {
    if (!data[field]) {
      errors.push(`${filePath}: Missing required field '${field}'`);
    }
  }
}

/**
 * Validate recommended fields
 */
function validateRecommendedFields(filePath, data) {
  for (const field of RECOMMENDED_FIELDS) {
    if (!data[field]) {
      warnings.push(`${filePath}: Missing recommended field '${field}'`);
    }
  }
}

/**
 * Validate enum values
 */
function validateEnums(filePath, data) {
  // Body type
  if (data.body && !ENUMS.body_type.includes(data.body)) {
    errors.push(`${filePath}: Invalid body type '${data.body}'. Must be one of: ${ENUMS.body_type.join(', ')}`);
  }
  
  // Battery chemistry
  if (data.battery?.chemistry && !ENUMS.battery_chemistry.includes(data.battery.chemistry)) {
    errors.push(`${filePath}: Invalid battery chemistry '${data.battery.chemistry}'. Must be one of: ${ENUMS.battery_chemistry.join(', ')}`);
  }
  
  // Drivetrain
  if (data.performance?.drivetrain && !ENUMS.drivetrain.includes(data.performance.drivetrain)) {
    errors.push(`${filePath}: Invalid drivetrain '${data.performance.drivetrain}'. Must be one of: ${ENUMS.drivetrain.join(', ')}`);
  }
  
  // DC speed class
  if (data.charging?.dc_speed_class && !ENUMS.dc_speed_class.includes(data.charging.dc_speed_class)) {
    errors.push(`${filePath}: Invalid DC speed class '${data.charging.dc_speed_class}'. Must be one of: ${ENUMS.dc_speed_class.join(', ')}`);
  }
  
  // Charging ports
  if (data.charging?.ac_port) {
    for (const port of data.charging.ac_port) {
      if (!ENUMS.charging_port_ac.includes(port)) {
        errors.push(`${filePath}: Invalid AC port '${port}'. Must be one of: ${ENUMS.charging_port_ac.join(', ')}`);
      }
    }
  }
  
  if (data.charging?.dc_port) {
    for (const port of data.charging.dc_port) {
      if (!ENUMS.charging_port_dc.includes(port)) {
        errors.push(`${filePath}: Invalid DC port '${port}'. Must be one of: ${ENUMS.charging_port_dc.join(', ')}`);
      }
    }
  }
  
  // Market availability status
  if (data.market_availability) {
    for (const market of data.market_availability) {
      if (!ENUMS.market_status.includes(market.status)) {
        errors.push(`${filePath}: Invalid market status '${market.status}'. Must be one of: ${ENUMS.market_status.join(', ')}`);
      }
      
      // Validate country code format
      if (!/^[A-Z]{2}$/.test(market.country)) {
        errors.push(`${filePath}: Invalid country code '${market.country}'. Must be ISO 3166-1 alpha-2 (e.g., 'DE', 'PL')`);
      }
    }
  }
  
  // Image types
  if (data.images) {
    for (const image of data.images) {
      if (!ENUMS.image_type.includes(image.type)) {
        errors.push(`${filePath}: Invalid image type '${image.type}'. Must be one of: ${ENUMS.image_type.join(', ')}`);
      }
      
      // Check required image fields
      if (!image.url) {
        errors.push(`${filePath}: Image missing required 'url' field`);
      }
      if (!image.alt) {
        warnings.push(`${filePath}: Image missing 'alt' text for accessibility`);
      }
    }
  }
}

/**
 * Validate data consistency
 */
function validateConsistency(filePath, data) {
  // Check that DC speed class matches actual DC power
  if (data.charging?.dc_max_kw && data.charging?.dc_speed_class) {
    const power = data.charging.dc_max_kw;
    const expectedClass = 
      power === 0 ? 'NONE' :
      power < 50 ? 'SLOW' :
      power < 100 ? 'MEDIUM' :
      power < 150 ? 'FAST' :
      power < 250 ? 'ULTRA_FAST' : 'HYPER_FAST';
    
    if (data.charging.dc_speed_class !== expectedClass) {
      warnings.push(`${filePath}: DC speed class '${data.charging.dc_speed_class}' may not match actual power ${power}kW (expected '${expectedClass}')`);
    }
  }
  
  // Warn if chemistry is OTHER but no chemistry_other specified
  if (data.battery?.chemistry === 'OTHER' && !data.battery?.chemistry_other) {
    warnings.push(`${filePath}: Battery chemistry is 'OTHER' but no chemistry_other field specified`);
  }
  
  // Check that discontinued markets have discontinued_on date
  if (data.market_availability) {
    for (const market of data.market_availability) {
      if (market.status === 'discontinued' && !market.discontinued_on) {
        warnings.push(`${filePath}: Market ${market.country} is discontinued but no discontinued_on date provided`);
      }
    }
  }
  
  // Validate segment format
  if (data.segment && !/^[ABCDEFMJS][AB]?$/.test(data.segment)) {
    errors.push(`${filePath}: Invalid segment '${data.segment}'. Must match pattern [ABCDEFMJS][AB]? (e.g., 'C', 'JB')`);
  }
  
  // Check logical consistency
  if (data.battery?.capacity_kwh && data.battery?.gross_capacity_kwh) {
    if (data.battery.capacity_kwh > data.battery.gross_capacity_kwh) {
      errors.push(`${filePath}: Usable capacity (${data.battery.capacity_kwh} kWh) cannot exceed gross capacity (${data.battery.gross_capacity_kwh} kWh)`);
    }
  }
}

/**
 * Validate image references
 */
function validateImages(filePath, data) {
  if (!data.images) {
    return;
  }
  
  const contentDir = path.dirname(filePath);
  const projectRoot = path.resolve(__dirname, '..');
  
  for (const image of data.images) {
    // Skip external URLs
    if (image.url.startsWith('http://') || image.url.startsWith('https://')) {
      continue;
    }
    
    // Check if local image file exists
    const imagePath = path.join(projectRoot, 'static', image.url);
    if (!fs.existsSync(imagePath)) {
      warnings.push(`${filePath}: Referenced image not found: ${image.url}`);
    }
  }
}

/**
 * Check for translations
 */
function checkTranslations(filePath, data) {
  const match = filePath.match(/content\/([a-z]{2})\//);
  if (!match) {
    return; // Not in a language-specific directory
  }
  
  const currentLang = match[1];
  const relPath = filePath.split(/content\/[a-z]{2}\//)[1];
  
  // Check if other language versions exist
  const languages = ['en', 'de', 'pl', 'fr', 'es'];
  const missingTranslations = [];
  
  for (const lang of languages) {
    if (lang === currentLang) continue;
    
    const translationPath = path.join(
      path.dirname(filePath).replace(`/content/${currentLang}/`, `/content/${lang}/`),
      path.basename(filePath)
    );
    
    if (!fs.existsSync(translationPath)) {
      missingTranslations.push(lang);
    }
  }
  
  if (missingTranslations.length > 0 && missingTranslations.length < languages.length - 1) {
    warnings.push(`${filePath}: Missing translations for: ${missingTranslations.join(', ')}`);
  }
}

/**
 * Find all vehicle markdown files
 */
function findVehicleFiles(dir) {
  const files = [];
  
  function walk(currentDir) {
    const entries = fs.readdirSync(currentDir, { withFileTypes: true });
    
    for (const entry of entries) {
      const fullPath = path.join(currentDir, entry.name);
      
      if (entry.isDirectory()) {
        walk(fullPath);
      } else if (entry.name.endsWith('.md') && fullPath.includes('/vehicles/')) {
        files.push(fullPath);
      }
    }
  }
  
  walk(dir);
  return files;
}

/**
 * Main validation function
 */
function validate() {
  const projectRoot = path.resolve(__dirname, '..');
  const contentDir = path.join(projectRoot, 'content');
  
  if (!fs.existsSync(contentDir)) {
    console.error(`Content directory not found: ${contentDir}`);
    process.exit(1);
  }
  
  const vehicleFiles = findVehicleFiles(contentDir);
  
  console.log(`Found ${vehicleFiles.length} vehicle files to validate\n`);
  
  for (const file of vehicleFiles) {
    const data = parseFrontMatter(file);
    
    if (!data) {
      continue; // Already logged error
    }
    
    validateRequiredFields(file, data);
    validateRecommendedFields(file, data);
    validateEnums(file, data);
    validateConsistency(file, data);
    validateImages(file, data);
    checkTranslations(file, data);
  }
  
  // Print results
  console.log('='.repeat(80));
  console.log('VALIDATION RESULTS');
  console.log('='.repeat(80));
  console.log();
  
  if (errors.length === 0 && warnings.length === 0) {
    console.log('✅ All validations passed!');
    process.exit(0);
  }
  
  if (errors.length > 0) {
    console.log(`❌ ${errors.length} ERROR(S) FOUND:\n`);
    errors.forEach(err => console.log(`  • ${err}`));
    console.log();
  }
  
  if (warnings.length > 0) {
    console.log(`⚠️  ${warnings.length} WARNING(S) FOUND:\n`);
    warnings.forEach(warn => console.log(`  • ${warn}`));
    console.log();
  }
  
  // Exit with error if there are errors (warnings are okay)
  process.exit(errors.length > 0 ? 1 : 0);
}

// Run validation
validate();
