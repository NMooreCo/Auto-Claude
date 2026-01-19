/**
 * ContentTaskFields - Fields for content/creative mode tasks
 *
 * Displays when a content-related category is selected (creative, game_design, worldbuilding, content_docs).
 * Allows users to specify content project type, target audience, and content type.
 */
import { useTranslation } from 'react-i18next';
import { Label } from '../ui/label';
import { Input } from '../ui/input';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue
} from '../ui/select';
import type { ContentProjectType } from '../../../shared/types';

// Project type options (values are used for translation key lookup)
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

interface ContentTaskFieldsProps {
  /** Current project type value */
  projectType: ContentProjectType | '';
  /** Current target audience value */
  targetAudience: string;
  /** Current content type value */
  contentType: string;
  /** Callback when project type changes */
  onProjectTypeChange: (value: ContentProjectType | '') => void;
  /** Callback when target audience changes */
  onTargetAudienceChange: (value: string) => void;
  /** Callback when content type changes */
  onContentTypeChange: (value: string) => void;
  /** Whether the fields are disabled */
  disabled?: boolean;
  /** Optional ID prefix for form elements (for accessibility) */
  idPrefix?: string;
}

export function ContentTaskFields({
  projectType,
  targetAudience,
  contentType,
  onProjectTypeChange,
  onTargetAudienceChange,
  onContentTypeChange,
  disabled = false,
  idPrefix = ''
}: ContentTaskFieldsProps) {
  const { t } = useTranslation('tasks');
  const prefix = idPrefix ? `${idPrefix}-` : '';

  return (
    <div className="space-y-4 p-4 rounded-lg border border-info/30 bg-info/5">
      <h4 className="text-sm font-medium text-foreground">
        {t('form.content.title')}
      </h4>

      {/* Project Type Dropdown */}
      <div className="space-y-2">
        <Label htmlFor={`${prefix}project-type`} className="text-xs font-medium text-muted-foreground">
          {t('form.content.projectType')}
        </Label>
        <Select
          value={projectType}
          onValueChange={(value) => onProjectTypeChange(value as ContentProjectType)}
          disabled={disabled}
        >
          <SelectTrigger id={`${prefix}project-type`} className="h-9">
            <SelectValue placeholder={t('form.content.selectProjectType')} />
          </SelectTrigger>
          <SelectContent>
            {PROJECT_TYPE_OPTIONS.map((value) => (
              <SelectItem key={value} value={value}>
                {t(`form.content.projectTypes.${value}`)}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>

      {/* Target Audience */}
      <div className="space-y-2">
        <Label htmlFor={`${prefix}target-audience`} className="text-xs font-medium text-muted-foreground">
          {t('form.content.targetAudience')}
        </Label>
        <Input
          id={`${prefix}target-audience`}
          placeholder={t('form.content.targetAudiencePlaceholder')}
          value={targetAudience}
          onChange={(e) => onTargetAudienceChange(e.target.value)}
          disabled={disabled}
          className="h-9"
        />
      </div>

      {/* Content Type */}
      <div className="space-y-2">
        <Label htmlFor={`${prefix}content-type`} className="text-xs font-medium text-muted-foreground">
          {t('form.content.contentType')}
        </Label>
        <Input
          id={`${prefix}content-type`}
          placeholder={t('form.content.contentTypePlaceholder')}
          value={contentType}
          onChange={(e) => onContentTypeChange(e.target.value)}
          disabled={disabled}
          className="h-9"
        />
      </div>
    </div>
  );
}
