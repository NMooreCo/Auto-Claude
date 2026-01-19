/**
 * Unit tests for Content Mode i18n translations (Phase 7)
 * Tests that all required translation keys exist in both English and French
 *
 * @vitest-environment node
 */
import { describe, it, expect, beforeAll } from 'vitest';
import * as fs from 'fs';
import * as path from 'path';

// Load translation files
let enTasks: Record<string, unknown>;
let frTasks: Record<string, unknown>;

beforeAll(() => {
  const localesDir = path.join(__dirname, '..', 'i18n', 'locales');
  enTasks = JSON.parse(fs.readFileSync(path.join(localesDir, 'en', 'tasks.json'), 'utf-8'));
  frTasks = JSON.parse(fs.readFileSync(path.join(localesDir, 'fr', 'tasks.json'), 'utf-8'));
});

// Helper to get nested property
function getNestedProperty(obj: Record<string, unknown>, path: string): unknown {
  return path.split('.').reduce((acc: unknown, part: string) => {
    if (acc && typeof acc === 'object' && part in (acc as Record<string, unknown>)) {
      return (acc as Record<string, unknown>)[part];
    }
    return undefined;
  }, obj);
}

describe('Content Mode i18n Translations (Phase 7)', () => {
  describe('English translations exist', () => {
    describe('Content category translations', () => {
      it('should have creative category translation', () => {
        const value = getNestedProperty(enTasks, 'form.classification.values.category.creative');
        expect(value).toBe('Creative');
      });

      it('should have game_design category translation', () => {
        const value = getNestedProperty(enTasks, 'form.classification.values.category.game_design');
        expect(value).toBe('Game Design');
      });

      it('should have worldbuilding category translation', () => {
        const value = getNestedProperty(enTasks, 'form.classification.values.category.worldbuilding');
        expect(value).toBe('Worldbuilding');
      });

      it('should have content_docs category translation', () => {
        const value = getNestedProperty(enTasks, 'form.classification.values.category.content_docs');
        expect(value).toBe('Content Docs');
      });
    });

    describe('Content form field translations', () => {
      it('should have content section title', () => {
        const value = getNestedProperty(enTasks, 'form.content.title');
        expect(value).toBe('Content Details');
      });

      it('should have projectType label', () => {
        const value = getNestedProperty(enTasks, 'form.content.projectType');
        expect(value).toBe('Project Type');
      });

      it('should have selectProjectType placeholder', () => {
        const value = getNestedProperty(enTasks, 'form.content.selectProjectType');
        expect(value).toBeDefined();
        expect(typeof value).toBe('string');
      });

      it('should have targetAudience label', () => {
        const value = getNestedProperty(enTasks, 'form.content.targetAudience');
        expect(value).toBe('Target Audience');
      });

      it('should have targetAudiencePlaceholder', () => {
        const value = getNestedProperty(enTasks, 'form.content.targetAudiencePlaceholder');
        expect(value).toBeDefined();
        expect(typeof value).toBe('string');
      });

      it('should have contentType label', () => {
        const value = getNestedProperty(enTasks, 'form.content.contentType');
        expect(value).toBe('Content Type');
      });

      it('should have contentTypePlaceholder', () => {
        const value = getNestedProperty(enTasks, 'form.content.contentTypePlaceholder');
        expect(value).toBeDefined();
        expect(typeof value).toBe('string');
      });
    });

    describe('Project type translations', () => {
      const projectTypes = [
        'card_game',
        'board_game',
        'ttrpg',
        'worldbuilding',
        'fiction',
        'business',
        'codebase_docs',
        'api_docs',
        'general'
      ];

      projectTypes.forEach(type => {
        it(`should have ${type} project type translation`, () => {
          const value = getNestedProperty(enTasks, `form.content.projectTypes.${type}`);
          expect(value).toBeDefined();
          expect(typeof value).toBe('string');
          expect((value as string).length).toBeGreaterThan(0);
        });
      });

      it('should have Card Game translation', () => {
        const value = getNestedProperty(enTasks, 'form.content.projectTypes.card_game');
        expect(value).toBe('Card Game');
      });

      it('should have Tabletop RPG translation', () => {
        const value = getNestedProperty(enTasks, 'form.content.projectTypes.ttrpg');
        expect(value).toBe('Tabletop RPG');
      });
    });
  });

  describe('French translations exist', () => {
    describe('Content category translations', () => {
      it('should have creative category translation', () => {
        const value = getNestedProperty(frTasks, 'form.classification.values.category.creative');
        expect(value).toBe('Créatif');
      });

      it('should have game_design category translation', () => {
        const value = getNestedProperty(frTasks, 'form.classification.values.category.game_design');
        expect(value).toBe('Conception de jeu');
      });

      it('should have worldbuilding category translation', () => {
        const value = getNestedProperty(frTasks, 'form.classification.values.category.worldbuilding');
        expect(value).toBe('Création d\'univers');
      });

      it('should have content_docs category translation', () => {
        const value = getNestedProperty(frTasks, 'form.classification.values.category.content_docs');
        expect(value).toBe('Docs de contenu');
      });
    });

    describe('Content form field translations', () => {
      it('should have content section title', () => {
        const value = getNestedProperty(frTasks, 'form.content.title');
        expect(value).toBeDefined();
        expect(typeof value).toBe('string');
      });

      it('should have projectType label', () => {
        const value = getNestedProperty(frTasks, 'form.content.projectType');
        expect(value).toBeDefined();
        expect(typeof value).toBe('string');
      });

      it('should have targetAudience label', () => {
        const value = getNestedProperty(frTasks, 'form.content.targetAudience');
        expect(value).toBeDefined();
        expect(typeof value).toBe('string');
      });

      it('should have contentType label', () => {
        const value = getNestedProperty(frTasks, 'form.content.contentType');
        expect(value).toBeDefined();
        expect(typeof value).toBe('string');
      });
    });

    describe('Project type translations', () => {
      const projectTypes = [
        'card_game',
        'board_game',
        'ttrpg',
        'worldbuilding',
        'fiction',
        'business',
        'codebase_docs',
        'api_docs',
        'general'
      ];

      projectTypes.forEach(type => {
        it(`should have ${type} project type translation`, () => {
          const value = getNestedProperty(frTasks, `form.content.projectTypes.${type}`);
          expect(value).toBeDefined();
          expect(typeof value).toBe('string');
          expect((value as string).length).toBeGreaterThan(0);
        });
      });
    });
  });

  describe('Translation parity', () => {
    describe('All English content keys exist in French', () => {
      it('should have matching content category keys', () => {
        const enCategories = getNestedProperty(enTasks, 'form.classification.values.category') as Record<string, string>;
        const frCategories = getNestedProperty(frTasks, 'form.classification.values.category') as Record<string, string>;

        const contentKeys = ['creative', 'game_design', 'worldbuilding', 'content_docs'];
        contentKeys.forEach(key => {
          expect(enCategories[key]).toBeDefined();
          expect(frCategories[key]).toBeDefined();
        });
      });

      it('should have matching content form field keys', () => {
        const enContent = getNestedProperty(enTasks, 'form.content') as Record<string, unknown>;
        const frContent = getNestedProperty(frTasks, 'form.content') as Record<string, unknown>;

        const fieldKeys = ['title', 'projectType', 'selectProjectType', 'targetAudience', 'targetAudiencePlaceholder', 'contentType', 'contentTypePlaceholder'];
        fieldKeys.forEach(key => {
          expect(enContent[key]).toBeDefined();
          expect(frContent[key]).toBeDefined();
        });
      });

      it('should have matching project type keys', () => {
        const enProjectTypes = getNestedProperty(enTasks, 'form.content.projectTypes') as Record<string, string>;
        const frProjectTypes = getNestedProperty(frTasks, 'form.content.projectTypes') as Record<string, string>;

        const typeKeys = ['card_game', 'board_game', 'ttrpg', 'worldbuilding', 'fiction', 'business', 'codebase_docs', 'api_docs', 'general'];
        typeKeys.forEach(key => {
          expect(enProjectTypes[key]).toBeDefined();
          expect(frProjectTypes[key]).toBeDefined();
        });
      });
    });

    describe('French translations are not identical to English', () => {
      it('should have different creative category translations', () => {
        const enValue = getNestedProperty(enTasks, 'form.classification.values.category.creative');
        const frValue = getNestedProperty(frTasks, 'form.classification.values.category.creative');
        expect(enValue).not.toBe(frValue);
      });

      it('should have different game_design category translations', () => {
        const enValue = getNestedProperty(enTasks, 'form.classification.values.category.game_design');
        const frValue = getNestedProperty(frTasks, 'form.classification.values.category.game_design');
        expect(enValue).not.toBe(frValue);
      });

      it('should have different worldbuilding category translations', () => {
        const enValue = getNestedProperty(enTasks, 'form.classification.values.category.worldbuilding');
        const frValue = getNestedProperty(frTasks, 'form.classification.values.category.worldbuilding');
        expect(enValue).not.toBe(frValue);
      });
    });
  });

  describe('Translation quality', () => {
    it('should have non-empty English translations for all content keys', () => {
      const contentSection = getNestedProperty(enTasks, 'form.content') as Record<string, unknown>;
      expect(contentSection).toBeDefined();

      // Check top-level string values
      const stringKeys = ['title', 'projectType', 'selectProjectType', 'targetAudience', 'targetAudiencePlaceholder', 'contentType', 'contentTypePlaceholder'];
      stringKeys.forEach(key => {
        const value = contentSection[key];
        expect(typeof value).toBe('string');
        expect((value as string).trim().length).toBeGreaterThan(0);
      });
    });

    it('should have non-empty French translations for all content keys', () => {
      const contentSection = getNestedProperty(frTasks, 'form.content') as Record<string, unknown>;
      expect(contentSection).toBeDefined();

      // Check top-level string values
      const stringKeys = ['title', 'projectType', 'selectProjectType', 'targetAudience', 'targetAudiencePlaceholder', 'contentType', 'contentTypePlaceholder'];
      stringKeys.forEach(key => {
        const value = contentSection[key];
        expect(typeof value).toBe('string');
        expect((value as string).trim().length).toBeGreaterThan(0);
      });
    });
  });
});
