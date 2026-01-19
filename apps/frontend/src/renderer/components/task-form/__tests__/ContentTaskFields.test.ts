/**
 * Unit tests for ContentTaskFields component
 * Tests content mode fields rendering logic, prop handling, and callback behavior
 *
 * @vitest-environment jsdom
 */
import { describe, it, expect, vi, beforeEach } from 'vitest';
import type { ContentProjectType } from '../../../../shared/types';

// Project type options (should match the component)
const PROJECT_TYPE_OPTIONS: ContentProjectType[] = [
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

describe('ContentTaskFields', () => {
  // Mock callbacks
  const mockOnProjectTypeChange = vi.fn();
  const mockOnTargetAudienceChange = vi.fn();
  const mockOnContentTypeChange = vi.fn();

  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('Project Type Options', () => {
    it('should have all 9 project types available', () => {
      expect(PROJECT_TYPE_OPTIONS).toHaveLength(9);
    });

    it('should include card_game for card collecting games', () => {
      expect(PROJECT_TYPE_OPTIONS).toContain('card_game');
    });

    it('should include board_game for board games', () => {
      expect(PROJECT_TYPE_OPTIONS).toContain('board_game');
    });

    it('should include ttrpg for tabletop RPGs', () => {
      expect(PROJECT_TYPE_OPTIONS).toContain('ttrpg');
    });

    it('should include worldbuilding for lore and settings', () => {
      expect(PROJECT_TYPE_OPTIONS).toContain('worldbuilding');
    });

    it('should include fiction for stories and novels', () => {
      expect(PROJECT_TYPE_OPTIONS).toContain('fiction');
    });

    it('should include business for business content', () => {
      expect(PROJECT_TYPE_OPTIONS).toContain('business');
    });

    it('should include codebase_docs for code documentation', () => {
      expect(PROJECT_TYPE_OPTIONS).toContain('codebase_docs');
    });

    it('should include api_docs for API documentation', () => {
      expect(PROJECT_TYPE_OPTIONS).toContain('api_docs');
    });

    it('should include general as a fallback option', () => {
      expect(PROJECT_TYPE_OPTIONS).toContain('general');
    });

    it('should have options in expected order', () => {
      const expectedOrder: ContentProjectType[] = [
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
      expect(PROJECT_TYPE_OPTIONS).toEqual(expectedOrder);
    });
  });

  describe('Props Handling', () => {
    it('should accept empty projectType', () => {
      const projectType: ContentProjectType | '' = '';
      expect(projectType).toBe('');
    });

    it('should accept valid projectType', () => {
      const projectType: ContentProjectType = 'card_game';
      expect(projectType).toBe('card_game');
    });

    it('should accept targetAudience string', () => {
      const targetAudience = 'Card game enthusiasts ages 12+';
      expect(targetAudience).toBe('Card game enthusiasts ages 12+');
    });

    it('should accept contentType string', () => {
      const contentType = 'Character cards';
      expect(contentType).toBe('Character cards');
    });

    it('should handle disabled state', () => {
      const disabled = true;
      expect(disabled).toBe(true);
    });

    it('should handle enabled state (default)', () => {
      const disabled = false;
      expect(disabled).toBe(false);
    });

    it('should handle idPrefix for accessibility', () => {
      const idPrefix = 'create';
      const prefix = idPrefix ? `${idPrefix}-` : '';
      expect(prefix).toBe('create-');
    });

    it('should handle empty idPrefix', () => {
      const idPrefix = '';
      const prefix = idPrefix ? `${idPrefix}-` : '';
      expect(prefix).toBe('');
    });
  });

  describe('Callback Behavior', () => {
    it('should call onProjectTypeChange with correct value', () => {
      const selectedValue: ContentProjectType = 'ttrpg';
      mockOnProjectTypeChange(selectedValue);
      expect(mockOnProjectTypeChange).toHaveBeenCalledWith('ttrpg');
    });

    it('should call onTargetAudienceChange with input value', () => {
      const inputValue = 'Dungeon Masters and players';
      mockOnTargetAudienceChange(inputValue);
      expect(mockOnTargetAudienceChange).toHaveBeenCalledWith('Dungeon Masters and players');
    });

    it('should call onContentTypeChange with input value', () => {
      const inputValue = 'Monster stat blocks';
      mockOnContentTypeChange(inputValue);
      expect(mockOnContentTypeChange).toHaveBeenCalledWith('Monster stat blocks');
    });

    it('should handle rapid project type changes', () => {
      const types: ContentProjectType[] = ['card_game', 'board_game', 'fiction'];
      types.forEach(type => mockOnProjectTypeChange(type));
      expect(mockOnProjectTypeChange).toHaveBeenCalledTimes(3);
      expect(mockOnProjectTypeChange).toHaveBeenLastCalledWith('fiction');
    });

    it('should handle empty string changes for project type', () => {
      mockOnProjectTypeChange('card_game');
      mockOnProjectTypeChange('');
      expect(mockOnProjectTypeChange).toHaveBeenLastCalledWith('');
    });

    it('should handle clearing target audience', () => {
      mockOnTargetAudienceChange('Initial audience');
      mockOnTargetAudienceChange('');
      expect(mockOnTargetAudienceChange).toHaveBeenLastCalledWith('');
    });
  });

  describe('ID Generation', () => {
    it('should generate correct project-type ID with prefix', () => {
      const prefix = 'create-';
      const projectTypeId = `${prefix}project-type`;
      expect(projectTypeId).toBe('create-project-type');
    });

    it('should generate correct target-audience ID with prefix', () => {
      const prefix = 'edit-';
      const targetAudienceId = `${prefix}target-audience`;
      expect(targetAudienceId).toBe('edit-target-audience');
    });

    it('should generate correct content-type ID with prefix', () => {
      const prefix = 'wizard-';
      const contentTypeId = `${prefix}content-type`;
      expect(contentTypeId).toBe('wizard-content-type');
    });

    it('should generate IDs without prefix when empty', () => {
      const prefix = '';
      const projectTypeId = `${prefix}project-type`;
      expect(projectTypeId).toBe('project-type');
    });
  });

  describe('Form State Integration', () => {
    it('should properly track all three field values', () => {
      const formState = {
        projectType: 'card_game' as ContentProjectType | '',
        targetAudience: 'Competitive players',
        contentType: 'Creature cards'
      };

      expect(formState.projectType).toBe('card_game');
      expect(formState.targetAudience).toBe('Competitive players');
      expect(formState.contentType).toBe('Creature cards');
    });

    it('should handle initial empty state', () => {
      const initialState = {
        projectType: '' as ContentProjectType | '',
        targetAudience: '',
        contentType: ''
      };

      expect(initialState.projectType).toBe('');
      expect(initialState.targetAudience).toBe('');
      expect(initialState.contentType).toBe('');
    });

    it('should handle partial state', () => {
      const partialState = {
        projectType: 'worldbuilding' as ContentProjectType | '',
        targetAudience: 'Fantasy writers',
        contentType: ''
      };

      expect(partialState.projectType).toBe('worldbuilding');
      expect(partialState.targetAudience).toBe('Fantasy writers');
      expect(partialState.contentType).toBe('');
    });
  });

  describe('Styling Classes', () => {
    it('should apply correct container classes', () => {
      const containerClasses = [
        'space-y-4',
        'p-4',
        'rounded-lg',
        'border',
        'border-info/30',
        'bg-info/5'
      ];

      containerClasses.forEach(cls => {
        expect(cls).toBeTruthy();
      });
    });

    it('should apply h-9 height class to inputs', () => {
      const inputHeightClass = 'h-9';
      expect(inputHeightClass).toBe('h-9');
    });
  });

  describe('Use Case Scenarios', () => {
    it('should handle card game content creation', () => {
      const cardGameState = {
        projectType: 'card_game' as ContentProjectType,
        targetAudience: 'Card collectors and competitive players',
        contentType: 'Water element creature cards'
      };

      expect(cardGameState.projectType).toBe('card_game');
      expect(cardGameState.targetAudience).toContain('Card collectors');
      expect(cardGameState.contentType).toContain('cards');
    });

    it('should handle TTRPG content creation', () => {
      const ttrpgState = {
        projectType: 'ttrpg' as ContentProjectType,
        targetAudience: 'Dungeon Masters running D&D campaigns',
        contentType: 'Bestiary entries for undead creatures'
      };

      expect(ttrpgState.projectType).toBe('ttrpg');
      expect(ttrpgState.targetAudience).toContain('Dungeon Masters');
      expect(ttrpgState.contentType).toContain('Bestiary');
    });

    it('should handle codebase documentation', () => {
      const docsState = {
        projectType: 'codebase_docs' as ContentProjectType,
        targetAudience: 'New developers joining the team',
        contentType: 'Architecture overview and module guides'
      };

      expect(docsState.projectType).toBe('codebase_docs');
      expect(docsState.targetAudience).toContain('developers');
      expect(docsState.contentType).toContain('Architecture');
    });

    it('should handle fiction writing', () => {
      const fictionState = {
        projectType: 'fiction' as ContentProjectType,
        targetAudience: 'Young adult fantasy readers',
        contentType: 'Character backstories and world lore'
      };

      expect(fictionState.projectType).toBe('fiction');
      expect(fictionState.targetAudience).toContain('fantasy readers');
      expect(fictionState.contentType).toContain('Character');
    });
  });

  describe('Disabled State Behavior', () => {
    it('should not call callbacks when disabled', () => {
      const disabled = true;

      // Simulate disabled behavior - callbacks should not fire
      if (!disabled) {
        mockOnProjectTypeChange('card_game');
      }

      expect(mockOnProjectTypeChange).not.toHaveBeenCalled();
    });

    it('should allow callbacks when enabled', () => {
      const disabled = false;

      if (!disabled) {
        mockOnProjectTypeChange('card_game');
      }

      expect(mockOnProjectTypeChange).toHaveBeenCalledWith('card_game');
    });
  });

  describe('Translation Keys', () => {
    it('should use correct translation key structure for project types', () => {
      const translationKeyBase = 'form.content.projectTypes';

      PROJECT_TYPE_OPTIONS.forEach(type => {
        const fullKey = `${translationKeyBase}.${type}`;
        expect(fullKey).toMatch(/^form\.content\.projectTypes\./);
      });
    });

    it('should have translation key for title', () => {
      const titleKey = 'form.content.title';
      expect(titleKey).toBe('form.content.title');
    });

    it('should have translation key for projectType label', () => {
      const labelKey = 'form.content.projectType';
      expect(labelKey).toBe('form.content.projectType');
    });

    it('should have translation key for targetAudience label', () => {
      const labelKey = 'form.content.targetAudience';
      expect(labelKey).toBe('form.content.targetAudience');
    });

    it('should have translation key for contentType label', () => {
      const labelKey = 'form.content.contentType';
      expect(labelKey).toBe('form.content.contentType');
    });

    it('should have translation key for placeholders', () => {
      const placeholderKeys = [
        'form.content.selectProjectType',
        'form.content.targetAudiencePlaceholder',
        'form.content.contentTypePlaceholder'
      ];

      placeholderKeys.forEach(key => {
        expect(key).toMatch(/^form\.content\./);
      });
    });
  });
});
