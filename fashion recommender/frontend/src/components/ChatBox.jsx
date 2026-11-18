import React, { useState, useRef, useEffect } from 'react';
import { Send, Sparkles, User, Bot, Loader2, ArrowRight } from 'lucide-react';
import { chatWithStylist } from '../services/api';
import { useApp } from '../context/AppContext';
import OutfitCard from './OutfitCard';

export default function ChatBox({ onMixMatch, onVisualize }) {
  const { userProfile, weatherData, showToast } = useApp();
  const [messages, setMessages] = useState([
    {
      role: 'assistant',
      content: `Welcome! I'm Aura, your personal fashion stylist. I've synced your style profile (${userProfile?.body_type || 'profile'} silhouette, ${userProfile?.preferred_fit || 'relaxed'} fit, and favorite ${userProfile?.favorite_colors?.slice(0, 3).join(', ') || 'neutral'} palette). Where are you headed or what aesthetic shall we create today?`,
      outfit: null,
      suggestions: [
        'I need an outfit for college tomorrow',
        'Curate a smart casual office look under ₹4,000',
        'Suggest something for a weekend date night',
        'Adapt an outfit for cold weather'
      ]
    }
  ]);
  const [inputMessage, setInputMessage] = useState('');
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, loading]);

  const handleSend = async (textToSend) => {
    const text = (textToSend || inputMessage).trim();
    if (!text || loading) return;

    setInputMessage('');
    const newHistory = [...messages, { role: 'user', content: text }];
    setMessages(newHistory);
    setLoading(true);

    try {
      const response = await chatWithStylist({
        message: text,
        conversation_history: newHistory.map(m => ({ role: m.role, content: m.content })),
        gender_override: userProfile?.gender,
        weather_override: weatherData?.condition,
        budget_max_override: userProfile?.budget_max
      });

      setMessages(prev => [
        ...prev,
        {
          role: 'assistant',
          content: response.reply,
          outfit: response.outfit_recommendation,
          suggestions: response.follow_up_suggestions || [],
          engine_used: response.engine_used
        }
      ]);
    } catch (err) {
      console.error('Chat error:', err);
      showToast('Stylist response failed. Please try again.', 'error');
      setMessages(prev => [
        ...prev,
        {
          role: 'assistant',
          content: "I'm having a brief connection hitch, but based on your profile, relaxed cotton tops and versatile chinos remain my top recommendation today!",
          suggestions: ['Try another request']
        }
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="glass-card" style={{
      display: 'flex',
      flexDirection: 'column',
      height: '740px',
      borderRadius: 'var(--radius-lg)',
      overflow: 'hidden',
      border: '1px solid var(--border-medium)'
    }}>
      {/* Chat Header */}
      <div style={{
        padding: '1rem 1.5rem',
        borderBottom: '1px solid var(--border-subtle)',
        background: 'rgba(15, 23, 42, 0.7)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
          <div style={{
            width: '38px',
            height: '38px',
            borderRadius: '50%',
            background: 'linear-gradient(135deg, #D4AF37 0%, #F59E0B 100%)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center'
          }}>
            <Bot size={20} color="#0A0D14" />
          </div>
          <div>
            <div style={{ fontWeight: 700, fontSize: '1rem' }}>Aura — AI Personal Stylist</div>
            <div style={{ fontSize: '0.72rem', color: 'var(--accent-emerald)', display: 'flex', alignItems: 'center', gap: '0.35rem' }}>
              <span style={{ width: '6px', height: '6px', borderRadius: '50%', background: 'var(--accent-emerald)' }}></span>
              Profile Synced: {userProfile?.name || 'Alex'} • {userProfile?.gender || 'Female'} • {userProfile?.aesthetic_preferences?.[0] || 'Casual'}
            </div>
          </div>
        </div>

        <div className="badge badge-gold" style={{ fontSize: '0.7rem' }}>
          DUAL-AI ENGINE
        </div>
      </div>

      {/* Message Stream */}
      <div style={{
        flexGrow: 1,
        overflowY: 'auto',
        padding: '1.5rem',
        display: 'flex',
        flexDirection: 'column',
        gap: '1.25rem'
      }}>
        {messages.map((m, idx) => {
          const isUser = m.role === 'user';
          return (
            <div
              key={idx}
              style={{
                display: 'flex',
                flexDirection: 'column',
                alignItems: isUser ? 'flex-end' : 'flex-start',
                gap: '0.5rem',
                maxWidth: '90%',
                alignSelf: isUser ? 'flex-end' : 'flex-start'
              }}
            >
              {/* Message Bubble */}
              <div style={{
                display: 'flex',
                gap: '0.75rem',
                flexDirection: isUser ? 'row-reverse' : 'row'
              }}>
                <div style={{
                  width: '32px',
                  height: '32px',
                  borderRadius: '50%',
                  background: isUser ? '#3B82F6' : 'rgba(212, 175, 55, 0.2)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  flexShrink: 0
                }}>
                  {isUser ? <User size={16} /> : <Bot size={16} color="var(--gold-light)" />}
                </div>

                <div style={{
                  background: isUser ? 'linear-gradient(135deg, #1E3A8A 0%, #1E40AF 100%)' : 'rgba(30, 41, 59, 0.8)',
                  padding: '1rem 1.25rem',
                  borderRadius: 'var(--radius-md)',
                  border: isUser ? '1px solid rgba(59, 130, 246, 0.4)' : '1px solid var(--border-subtle)',
                  color: 'var(--text-primary)',
                  fontSize: '0.92rem',
                  lineHeight: 1.5,
                  boxShadow: 'var(--shadow-sm)'
                }}>
                  {m.content}
                </div>
              </div>

              {/* Embedded Interactive Outfit Card if Recommended */}
              {m.outfit && (
                <div style={{ width: '100%', marginTop: '0.5rem' }}>
                  <OutfitCard
                    outfit={m.outfit}
                    onMixMatch={onMixMatch}
                    onVisualize={onVisualize}
                  />
                </div>
              )}

              {/* Follow-up Prompt Pills */}
              {m.suggestions && m.suggestions.length > 0 && !isUser && idx === messages.length - 1 && (
                <div style={{
                  display: 'flex',
                  flexWrap: 'wrap',
                  gap: '0.4rem',
                  marginTop: '0.5rem',
                  marginLeft: '40px'
                }}>
                  {m.suggestions.map((sug, sIdx) => (
                    <button
                      key={sIdx}
                      onClick={() => handleSend(sug)}
                      style={{
                        background: 'rgba(255, 255, 255, 0.05)',
                        border: '1px solid var(--border-subtle)',
                        color: 'var(--gold-light)',
                        padding: '0.35rem 0.8rem',
                        borderRadius: 'var(--radius-full)',
                        fontSize: '0.78rem',
                        display: 'flex',
                        alignItems: 'center',
                        gap: '0.3rem',
                        transition: 'all 0.2s ease'
                      }}
                      onMouseEnter={(e) => e.currentTarget.style.borderColor = 'var(--gold-light)'}
                      onMouseLeave={(e) => e.currentTarget.style.borderColor = 'var(--border-subtle)'}
                    >
                      <span>{sug}</span>
                      <ArrowRight size={12} />
                    </button>
                  ))}
                </div>
              )}
            </div>
          );
        })}

        {loading && (
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', color: 'var(--text-secondary)' }}>
            <Loader2 size={20} className="animate-spin" color="var(--gold-light)" />
            <span style={{ fontSize: '0.85rem' }}>Aura is styling and coordinating your look...</span>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <div style={{
        padding: '1rem 1.5rem',
        borderTop: '1px solid var(--border-subtle)',
        background: 'rgba(15, 23, 42, 0.7)',
        display: 'flex',
        gap: '0.75rem',
        alignItems: 'center'
      }}>
        <input
          type="text"
          value={inputMessage}
          onChange={(e) => setInputMessage(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && handleSend()}
          placeholder="E.g. I need something for college tomorrow under ₹2,000..."
          disabled={loading}
          style={{
            flexGrow: 1,
            background: 'rgba(255, 255, 255, 0.05)',
            border: '1px solid var(--border-subtle)',
            padding: '0.75rem 1.25rem',
            borderRadius: 'var(--radius-full)',
            color: 'var(--text-primary)',
            fontSize: '0.92rem',
            outline: 'none',
            transition: 'border-color 0.2s ease'
          }}
          onFocus={(e) => e.target.style.borderColor = 'var(--gold-primary)'}
          onBlur={(e) => e.target.style.borderColor = 'var(--border-subtle)'}
        />
        <button
          onClick={() => handleSend()}
          disabled={loading || !inputMessage.trim()}
          className="btn-primary"
          style={{ padding: '0.75rem 1.25rem', borderRadius: 'var(--radius-full)' }}
        >
          <Send size={16} />
          <span>Send</span>
        </button>
      </div>
    </div>
  );
}
