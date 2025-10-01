import { cn } from '@/lib/utils'

describe('cn utility function', () => {
  it('should merge class names correctly', () => {
    const result = cn('class1', 'class2')
    expect(result).toContain('class1')
    expect(result).toContain('class2')
  })

  it('should handle conditional classes', () => {
    const result = cn('base', true && 'conditional', false && 'hidden')
    expect(result).toContain('base')
    expect(result).toContain('conditional')
    expect(result).not.toContain('hidden')
  })

  it('should handle tailwind merge conflicts', () => {
    const result = cn('p-4', 'p-2')
    // Should only keep the last padding class
    expect(result).toBe('p-2')
  })

  it('should handle empty input', () => {
    const result = cn()
    expect(result).toBe('')
  })

  it('should handle undefined and null values', () => {
    const result = cn('class1', undefined, null, 'class2')
    expect(result).toContain('class1')
    expect(result).toContain('class2')
  })

  it('should handle arrays of classes', () => {
    const result = cn(['class1', 'class2'], 'class3')
    expect(result).toContain('class1')
    expect(result).toContain('class2')
    expect(result).toContain('class3')
  })

  it('should handle objects with conditional classes', () => {
    const result = cn({
      'class1': true,
      'class2': false,
      'class3': true
    })
    expect(result).toContain('class1')
    expect(result).not.toContain('class2')
    expect(result).toContain('class3')
  })
})
