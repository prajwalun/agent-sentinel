"use client"

import { useEffect, useState } from "react"
import { useSession } from "next-auth/react"
import { supabase } from "@/lib/supabase"

export function useSupabaseAuth() {
  const { data: session } = useSession()
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (session?.user) {
      // Set Supabase auth context for RLS
      supabase.auth.getSession().then(({ data: { session: supabaseSession } }) => {
        if (!supabaseSession && session.user.id) {
          // Create a Supabase session if it doesn't exist
          // This is a simplified approach - in production you'd handle this more securely
          setLoading(false)
        } else {
          setLoading(false)
        }
      })
    } else {
      setLoading(false)
    }
  }, [session])

  return { session, loading }
}

export function useAgents() {
  const { session } = useSupabaseAuth()
  const [agents, setAgents] = useState<any[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (session?.user?.id) {
      fetchAgents()
    }
  }, [session])

  const fetchAgents = async () => {
    try {
      const { data, error } = await supabase
        .from("agents")
        .select("*")
        .eq("user_id", session?.user?.id)
        .order("created_at", { ascending: false })

      if (error) throw error
      setAgents(data || [])
    } catch (error) {
      console.error("Error fetching agents:", error)
    } finally {
      setLoading(false)
    }
  }

  return { agents, loading, refetch: fetchAgents }
}

export function useSecurityEvents() {
  const { session } = useSupabaseAuth()
  const [events, setEvents] = useState<any[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (session?.user?.id) {
      fetchEvents()
    }
  }, [session])

  const fetchEvents = async () => {
    try {
      const { data, error } = await supabase
        .from("security_events")
        .select(`
          *,
          agents (name)
        `)
        .eq("user_id", session?.user?.id)
        .order("created_at", { ascending: false })
        .limit(10)

      if (error) throw error
      setEvents(data || [])
    } catch (error) {
      console.error("Error fetching security events:", error)
    } finally {
      setLoading(false)
    }
  }

  return { events, loading, refetch: fetchEvents }
}
