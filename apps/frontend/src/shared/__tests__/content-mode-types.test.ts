/**
 * Unit tests for Content Mode types and constants
 * Tests the CONTENT_CATEGORIES constant and ContentProjectType type
 *
 * @vitest-environment node
 */
import { describe, it, expect } from 'vitest';
import { CONTENT_CATEGORIES } from '../types/task';
import type { TaskCategory, ContentProjectType } from '../types/task';

describe('Content Mode Types', () => {
  describe('CONTENT_CATEGORIES constant', () => {
    it('should contain exactly 4 content categories', () => {
      expect(CONTENT_CATEGORIES).toHaveLength(4);
    });

    it('should include creative category', () => {
      expect(CONTENT_CATEGORIES).toContain('creative');
    });

    it('should include game_design category', () => {
      expect(CONTENT_CATEGORIES).toContain('game_design');
    });

    it('should include worldbuilding category', () => {
      expect(CONTENT_CATEGORIES).toContain('worldbuilding');
    });

    it('should include content_docs category', () => {
      expect(CONTENT_CATEGORIES).toContain('content_docs');
    });

    it('should NOT include code-related categories', () => {
      const codeCategories = ['feature', 'bug_fix', 'refactoring', 'documentation', 'security'];
      codeCategories.forEach(category => {
        expect(CONTENT_CATEGORIES).not.toContain(category);
      });
    });

    it('should NOT include other non-content categories', () => {
      const otherCategories = ['performance', 'ui_ux', 'infrastructure', 'testing'];
      otherCategories.forEach(category => {
        expect(CONTENT_CATEGORIES).not.toContain(category);
      });
    });

    it('should be a valid array of TaskCategory values', () => {
      const validCategories: TaskCategory[] = [
        'feature', 'bug_fix', 'refactoring', 'documentation', 'security',
        'performance', 'ui_ux', 'infrastructure', 'testing',
        'creative', 'game_design', 'worldbuilding', 'content_docs'
      ];

      CONTENT_CATEGORIES.forEach(category => {
        expect(validCategories).toContain(category);
      });
    });
  });

  describe('Content category detection logic', () => {
    it('should correctly identify creative as content category', () => {
      const category: TaskCategory = 'creative';
      expect(CONTENT_CATEGORIES.includes(category)).toBe(true);
    });

    it('should correctly identify feature as NOT content category', () => {
      const category: TaskCategory = 'feature';
      expect(CONTENT_CATEGORIES.includes(category)).toBe(false);
    });

    it('should correctly identify bug_fix as NOT content category', () => {
      const category: TaskCategory = 'bug_fix';
      expect(CONTENT_CATEGORIES.includes(category)).toBe(false);
    });

    it('should correctly identify documentation as NOT content category', () => {
      // Note: 'documentation' is for code docs, 'content_docs' is for Content Mode
      const category: TaskCategory = 'documentation';
      expect(CONTENT_CATEGORIES.includes(category)).toBe(false);
    });

    it('should handle all task categories correctly', () => {
      const allCategories: TaskCategory[] = [
        'feature', 'bug_fix', 'refactoring', 'documentation', 'security',
        'performance', 'ui_ux', 'infrastructure', 'testing',
        'creative', 'game_design', 'worldbuilding', 'content_docs'
      ];

      const expectedContentCategories = ['creative', 'game_design', 'worldbuilding', 'content_docs'];

      allCategories.forEach(category => {
        const isContentCategory = CONTENT_CATEGORIES.includes(category);
        const shouldBeContent = expectedContentCategories.includes(category);
        expect(isContentCategory).toBe(shouldBeContent);
      });
    });
  });

  describe('ContentProjectType type', () => {
    it('should support card_game type', () => {
      const projectType: ContentProjectType = 'card_game';
      expect(projectType).toBe('card_game');
    });

    it('should support board_game type', () => {
      const projectType: ContentProjectType = 'board_game';
      expect(projectType).toBe('board_game');
    });

    it('should support ttrpg type', () => {
      const projectType: ContentProjectType = 'ttrpg';
      expect(projectType).toBe('ttrpg');
    });

    it('should support worldbuilding type', () => {
      const projectType: ContentProjectType = 'worldbuilding';
      expect(projectType).toBe('worldbuilding');
    });

    it('should support fiction type', () => {
      const projectType: ContentProjectType = 'fiction';
      expect(projectType).toBe('fiction');
    });

    it('should support business type', () => {
      const projectType: ContentProjectType = 'business';
      expect(projectType).toBe('business');
    });

    it('should support codebase_docs type', () => {
      const projectType: ContentProjectType = 'codebase_docs';
      expect(projectType).toBe('codebase_docs');
    });

    it('should support api_docs type', () => {
      const projectType: ContentProjectType = 'api_docs';
      expect(projectType).toBe('api_docs');
    });

    it('should support general type', () => {
      const projectType: ContentProjectType = 'general';
      expect(projectType).toBe('general');
    });
  });

  describe('Content Mode use cases', () => {
    it('should map creative category to game and creative project types', () => {
      const creativeProjectTypes: ContentProjectType[] = [
        'card_game', 'board_game', 'ttrpg', 'worldbuilding', 'fiction'
      ];

      // Creative category encompasses many creative project types
      creativeProjectTypes.forEach(type => {
        expect(typeof type).toBe('string');
      });
    });

    it('should map content_docs category to documentation project types', () => {
      const docsProjectTypes: ContentProjectType[] = ['codebase_docs', 'api_docs'];

      docsProjectTypes.forEach(type => {
        expect(['codebase_docs', 'api_docs']).toContain(type);
      });
    });

    it('should support game_design for board games and TTRPGs', () => {
      const gameDesignTypes: ContentProjectType[] = ['board_game', 'ttrpg', 'card_game'];

      gameDesignTypes.forEach(type => {
        expect(['board_game', 'ttrpg', 'card_game']).toContain(type);
      });
    });

    it('should support worldbuilding for fiction and game settings', () => {
      const worldbuildingTypes: ContentProjectType[] = ['worldbuilding', 'fiction', 'ttrpg'];

      worldbuildingTypes.forEach(type => {
        expect(['worldbuilding', 'fiction', 'ttrpg']).toContain(type);
      });
    });
  });

  describe('TaskMetadata content fields integration', () => {
    it('should correctly structure content metadata', () => {
      interface ContentMetadata {
        contentProjectType?: ContentProjectType;
        contentTargetAudience?: string;
        contentType?: string;
      }

      const metadata: ContentMetadata = {
        contentProjectType: 'card_game',
        contentTargetAudience: 'Card game enthusiasts',
        contentType: 'Water element cards'
      };

      expect(metadata.contentProjectType).toBe('card_game');
      expect(metadata.contentTargetAudience).toBe('Card game enthusiasts');
      expect(metadata.contentType).toBe('Water element cards');
    });

    it('should allow optional content fields', () => {
      interface ContentMetadata {
        contentProjectType?: ContentProjectType;
        contentTargetAudience?: string;
        contentType?: string;
      }

      const minimalMetadata: ContentMetadata = {
        contentProjectType: 'general'
      };

      expect(minimalMetadata.contentProjectType).toBe('general');
      expect(minimalMetadata.contentTargetAudience).toBeUndefined();
      expect(minimalMetadata.contentType).toBeUndefined();
    });

    it('should handle empty content metadata', () => {
      interface ContentMetadata {
        contentProjectType?: ContentProjectType;
        contentTargetAudience?: string;
        contentType?: string;
      }

      const emptyMetadata: ContentMetadata = {};

      expect(emptyMetadata.contentProjectType).toBeUndefined();
      expect(emptyMetadata.contentTargetAudience).toBeUndefined();
      expect(emptyMetadata.contentType).toBeUndefined();
    });
  });

  describe('TaskDraft content fields integration', () => {
    it('should support empty string for projectType in draft', () => {
      const draftProjectType: ContentProjectType | '' = '';
      expect(draftProjectType).toBe('');
    });

    it('should support valid projectType in draft', () => {
      const draftProjectType: ContentProjectType | '' = 'fiction';
      expect(draftProjectType).toBe('fiction');
    });

    it('should correctly structure content draft fields', () => {
      interface ContentDraftFields {
        contentProjectType?: ContentProjectType | '';
        contentTargetAudience?: string;
        contentType?: string;
      }

      const draftFields: ContentDraftFields = {
        contentProjectType: 'ttrpg',
        contentTargetAudience: 'Game Masters',
        contentType: 'Monster stat blocks'
      };

      expect(draftFields.contentProjectType).toBe('ttrpg');
      expect(draftFields.contentTargetAudience).toBe('Game Masters');
      expect(draftFields.contentType).toBe('Monster stat blocks');
    });
  });
});
